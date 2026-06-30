import json
import os
from typing import Any, AsyncGenerator, Dict, List

import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel

from ..data_layer.personalisation import build_personalisation_profile
from .prompt import get_system_prompt
from .tools import AGENT_TOOLS, TOOLS_REGISTRY

logger = structlog.get_logger("equitie_backend.agent")

# We will use OpenRouter or direct OpenAI. For standard interface we use OpenAI client.
# The base URL can be overridden via OPENAI_BASE_URL env var to point to OpenRouter.
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "dummy"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o-mini")


class Message(BaseModel):
    role: str
    content: str | None = None
    tool_calls: List[Any] | None = None
    tool_call_id: str | None = None


async def run_agent_loop(
    investor_id: str, messages: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    """
    Implement OpenRouter/OpenAI loop to manage conversation state.
    Supports max 5 tool calls to prevent infinite loops.
    Yields string tokens for SSE streaming.
    """
    # 1. Build Personalisation Profile
    profile = build_personalisation_profile(investor_id)
    sys_prompt = get_system_prompt(investor_id, profile)

    current_messages = [{"role": "system", "content": sys_prompt}] + messages

    max_loops = 5
    loop_count = 0

    while loop_count < max_loops:
        loop_count += 1

        try:
            tools: Any = AGENT_TOOLS
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=current_messages,
                tools=tools,
                stream=True,
                stream_options={"include_usage": True},
            )

            tool_calls: Dict[int, Dict[str, Any]] = {}
            content = ""

            async for chunk in response:  # type: ignore[union-attr]
                # Yield content tokens directly
                if getattr(chunk, "usage", None) is not None:
                    yield (
                        json.dumps(
                            {
                                "type": "usage",
                                "prompt_tokens": chunk.usage.prompt_tokens,
                                "completion_tokens": chunk.usage.completion_tokens,
                            }
                        )
                        + "\n"
                    )

                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    content += delta.content
                    yield json.dumps({"type": "content", "token": delta.content}) + "\n"

                # Collect tool calls
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index not in tool_calls:
                            tool_calls[tc.index] = {
                                "id": tc.id,
                                "function": {
                                    "name": tc.function.name if tc.function else "",
                                    "arguments": tc.function.arguments
                                    if tc.function and tc.function.arguments
                                    else "",
                                },
                            }
                        else:
                            if tc.function and tc.function.arguments:
                                tool_calls[tc.index]["function"]["arguments"] += (
                                    tc.function.arguments
                                )

            if not tool_calls:
                # Agent didn't call any tools, we are done
                break

            # Process Tool Calls
            tool_calls_list = list(tool_calls.values())

            # Format tool call message for history
            assistant_msg = {
                "role": "assistant",
                "content": content if content else None,
                "tool_calls": [
                    {
                        "id": tc_dict["id"],
                        "type": "function",
                        "function": {
                            "name": tc_dict["function"]["name"],
                            "arguments": tc_dict["function"]["arguments"],
                        },
                    }
                    for tc_dict in tool_calls_list
                ],
            }
            current_messages.append(assistant_msg)

            # Execute Tools
            for tc_dict in tool_calls_list:
                func_name = tc_dict["function"]["name"]
                args_str = tc_dict["function"]["arguments"]
                tool_call_id = tc_dict["id"]

                logger.info("Executing tool", function=func_name, arguments=args_str)
                yield (
                    json.dumps(
                        {
                            "type": "tool_call",
                            "function": func_name,
                            "arguments": args_str,
                        }
                    )
                    + "\n"
                )

                try:
                    args = json.loads(args_str) if args_str else {}
                    # Enforce investor_id if present in args
                    if "investor_id" in args and args["investor_id"] != investor_id:
                        logger.warning(
                            "Cross-tenant violation attempt blocked",
                            requested=args["investor_id"],
                            actual=investor_id,
                        )
                        args["investor_id"] = investor_id

                    if func_name in TOOLS_REGISTRY:
                        result = TOOLS_REGISTRY[func_name](**args)  # type: ignore[operator]
                    else:
                        result = {"error": f"Unknown tool: {func_name}"}
                except Exception as e:
                    logger.error(
                        "Tool execution failed", error=str(e), function=func_name
                    )
                    result = {"error": f"Execution failed: {str(e)}"}

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": func_name,
                    "content": json.dumps(result),
                }
                current_messages.append(tool_msg)

        except Exception as e:
            logger.error("Agent loop error", error=str(e))
            yield (
                json.dumps({"type": "error", "message": "An internal error occurred."})
                + "\n"
            )
            break

    if loop_count >= max_loops:
        yield (
            json.dumps({"type": "error", "message": "Reached maximum reasoning steps."})
            + "\n"
        )
