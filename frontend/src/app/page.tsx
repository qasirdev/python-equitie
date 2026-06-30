"use client";

import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Loader2, Activity, User, Info, FileText } from "lucide-react";

type Message = {
  role: "user" | "assistant" | "system" | "tool";
  content?: string;
  tool_calls?: unknown[];
  name?: string;
};

export default function Home() {
  const [investors, setInvestors] = useState<{ investor_id: string; investor_name: string }[]>([]);
  const [selectedInvestor, setSelectedInvestor] = useState<string>("INV-001");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Observability state
  const [latency, setLatency] = useState<number>(0);
  const [usage, setUsage] = useState({ prompt: 0, completion: 0 });
  const [toolCalls, setToolCalls] = useState<{function: string, arguments: string}[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch investors for dropdown
    fetch("http://127.0.0.1:8000/api/v1/investors")
      .then((res) => res.json())
      .then((data) => setInvestors(data))
      .catch((err) => console.error("Failed to load investors", err));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedInvestor) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setLatency(0);

    // Reset observability for new request
    setUsage({ prompt: 0, completion: 0 });
    setToolCalls([]);

    const startTime = Date.now();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          investor_id: selectedInvestor,
          messages: [...messages, userMessage],
        }),
      });

      if (!res.ok) throw new Error("Network response was not ok");
      if (!res.body) throw new Error("No readable stream");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      // Add empty assistant message placeholder
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.trim().length > 0);

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.type === "content") {
              assistantContent += data.token;
              setMessages((prev) => {
                const newMsgs = [...prev];
                newMsgs[newMsgs.length - 1].content = assistantContent;
                return newMsgs;
              });
            } else if (data.type === "tool_call") {
              setToolCalls((prev) => [...prev, { function: data.function, arguments: data.arguments }]);
            } else if (data.type === "usage") {
              setUsage((prev) => ({
                prompt: prev.prompt + data.prompt_tokens,
                completion: prev.completion + data.completion_tokens,
              }));
            } else if (data.type === "error") {
              setMessages((prev) => [...prev, { role: "assistant", content: `**Error:** ${data.message}` }]);
            }
          } catch (_err) {
            // not valid JSON, ignore
          }
        }
      }

      setLatency(Date.now() - startTime);

    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "assistant", content: "**Error connecting to server.**" }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate cost based on gpt-4o-mini pricing ($0.15/1M input, $0.60/1M output)
  const cost = ((usage.prompt / 1000000) * 0.15) + ((usage.completion / 1000000) * 0.60);

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar / Observability */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Activity className="text-indigo-600" /> EquiTie Agent
          </h1>
          <p className="text-sm text-slate-500 mt-1">SaaS Production Prototype</p>
        </div>

        <div className="p-6 border-b border-slate-200">
          <label className="text-sm font-semibold mb-2 block">Simulate Investor Login</label>
          <div className="relative">
            <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <select
              className="w-full pl-9 pr-4 py-2 border rounded-md bg-slate-50 focus:ring-2 focus:ring-indigo-500"
              value={selectedInvestor}
              onChange={(e) => setSelectedInvestor(e.target.value)}
            >
              <option value="">Select Investor...</option>
              {investors.map((inv) => (
                <option key={inv.investor_id} value={inv.investor_id}>
                  {inv.investor_name} ({inv.investor_id})
                </option>
              ))}
              <option value="INV-001">INV-001 (Fallback)</option>
              <option value="INV-002">INV-002 (Fallback)</option>
            </select>
          </div>
        </div>

        <div className="p-6 flex-1 overflow-y-auto">
          <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Info className="h-4 w-4" /> Observability Badge
          </h2>
          <div className="space-y-4">
            <div className="bg-slate-50 p-3 rounded-md border border-slate-100 flex justify-between items-center">
              <div className="text-xs text-slate-500 uppercase tracking-wider">Latency</div>
              <div className="font-mono text-sm">{latency} ms</div>
            </div>

            <div className="bg-slate-50 p-3 rounded-md border border-slate-100">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Tokens & Cost</div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Prompt:</span>
                <span className="font-mono">{usage.prompt}</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-slate-600">Completion:</span>
                <span className="font-mono">{usage.completion}</span>
              </div>
              <div className="flex justify-between text-sm font-semibold border-t border-slate-200 pt-2">
                <span>Est. Cost:</span>
                <span className="font-mono">${cost.toFixed(6)}</span>
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded-md border border-slate-100">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Tool Calls / Citations</div>
              {toolCalls.length === 0 ? (
                <div className="text-sm text-slate-400 italic">No tools called yet</div>
              ) : (
                <ul className="text-xs space-y-2">
                  {toolCalls.map((tc, i) => (
                    <li key={i} className="bg-indigo-50 border border-indigo-100 p-2 rounded flex flex-col gap-1">
                      <div className="flex items-center gap-1 font-mono text-indigo-700 font-semibold">
                        <FileText className="h-3 w-3" /> {tc.function}
                      </div>
                      <div className="font-mono text-[10px] text-slate-500 truncate" title={tc.arguments}>
                        {tc.arguments}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-50/50 relative">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4">
              <Activity className="h-12 w-12 text-slate-300" />
              <p>Select an investor and ask about their portfolio.</p>
              <div className="flex gap-2 mt-8">
                <button onClick={() => setInput("What is my current MOIC?")} className="px-4 py-2 bg-white border rounded-full text-sm hover:border-indigo-500 transition">What is my current MOIC?</button>
                <button onClick={() => setInput("Show me my upcoming capital calls.")} className="px-4 py-2 bg-white border rounded-full text-sm hover:border-indigo-500 transition">Upcoming capital calls?</button>
              </div>
            </div>
          ) : (
            messages.filter(m => m.role === "user" || m.role === "assistant").map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-2xl p-4 rounded-2xl ${msg.role === "user" ? "bg-indigo-600 text-white rounded-br-none shadow-sm" : "bg-white border border-slate-200 text-slate-800 rounded-bl-none shadow-sm"}`}>
                  <div className="prose prose-sm prose-slate max-w-none">
                    <ReactMarkdown>
                      {msg.content || ""}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-bl-none shadow-sm">
                <Loader2 className="h-5 w-5 animate-spin text-indigo-600" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white border-t border-slate-200">
          <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your portfolio..."
              className="flex-1 px-6 py-4 rounded-full border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-slate-50 shadow-inner"
              disabled={isLoading || !selectedInvestor}
            />
            <button
              type="submit"
              disabled={isLoading || !selectedInvestor || !input.trim()}
              className="absolute right-2 top-2 bottom-2 aspect-square bg-indigo-600 text-white rounded-full flex items-center justify-center hover:bg-indigo-700 disabled:opacity-50 transition shadow-md"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
