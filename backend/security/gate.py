import re

import structlog
from fastapi import HTTPException

logger = structlog.get_logger("equitie_backend.security")


class PromptInjectionDetector:
    """
    Basic security gate to detect prompt injection and off-topic queries.
    """

    # Financial domain keywords to ensure queries are on-topic
    FINANCIAL_KEYWORDS = {
        "portfolio",
        "deal",
        "company",
        "moic",
        "dpi",
        "rvpi",
        "value",
        "cost",
        "basis",
        "distribution",
        "fee",
        "call",
        "capital",
        "fund",
        "return",
        "invest",
        "share",
        "price",
        "valuation",
        "exit",
        "account",
    }

    # Patterns common in prompt injection attempts
    INJECTION_PATTERNS = [
        r"(?i)(ignore|disregard|forget)\s+(all\s+)?(previous\s+)?(instructions|rules|prompts)",
        r"(?i)you\s+are\s+now",
        r"(?i)system\s+prompt",
        r"(?i)translate\s+this",
        r"(?i)bypass",
    ]

    @classmethod
    def check_query(cls, query: str) -> None:
        """
        Check if a query is safe and on-topic.
        Raises HTTPException if a violation is detected.
        """
        # 1. Detect Injection
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, query):
                logger.warning(
                    "Prompt injection detected", query=query, pattern=pattern
                )
                raise HTTPException(
                    status_code=400, detail="Query violates security policies."
                )

        # 2. Enforce On-Topic (Simple heuristic)
        # For a production system this could be an LLM classification step or embeddings check.
        # Here we just check if it contains any financial keywords or is a very short query (like "hi").
        # Skip this simple check for short queries or greetings
        if len(query.split()) > 3:
            words = set(re.findall(r"\b\w+\b", query.lower()))
            if not words.intersection(cls.FINANCIAL_KEYWORDS):
                # If they ask something totally unrelated like "What is the capital of France?"
                logger.warning("Off-topic query blocked", query=query)
                raise HTTPException(
                    status_code=400,
                    detail="Query must be related to your portfolio or investments.",
                )
