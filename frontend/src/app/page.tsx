"use client";

import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Loader2, Activity, User, ChevronRight, Zap, Database, BarChart3, Clock, Sparkles, Trash2, Mic, MicOff } from "lucide-react";

type Message = {
  role: "user" | "assistant" | "system" | "tool";
  content?: string;
  tool_calls?: unknown[];
  name?: string;
};

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}



interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface SpeechRecognitionResultList {
  length: number;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare class SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

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

  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Voice input state
  const [isListening, setIsListening] = useState(false);
  const [isSpeechSupported, setIsSpeechSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Initialize Web Speech API
    if (typeof window !== "undefined") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognition.onresult = (event: any) => {
          let transcript = "";
          for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
          }
          setInput(transcript);
        };

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onerror = () => setIsListening(false);

        recognitionRef.current = recognition;
        // eslint-disable-next-line
        setIsSpeechSupported(true);
      }
    }
  }, []);

  const toggleListen = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setInput("");
      recognitionRef.current?.start();
    }
  };

  useEffect(() => {
    // Fetch investors for dropdown
    fetch("/api/v1/investors")
      .then((res) => res.json())
      .then((data) => setInvestors(data))
      .catch((err) => console.error("Failed to load investors", err));
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: "smooth"
      });
    }
  }, [messages]);

  const clearChat = () => {
    setMessages([]);
    setUsage({ prompt: 0, completion: 0 });
    setToolCalls([]);
    setLatency(0);
  };

  // Reset chat whenever the selected investor changes
  useEffect(() => {
    // eslint-disable-next-line
    setMessages([]);
    setUsage({ prompt: 0, completion: 0 });
    setToolCalls([]);
    setLatency(0);
  }, [selectedInvestor]);

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
      const res = await fetch("/api/v1/chat", {
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
          } catch (_err) { // eslint-disable-line
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
    <div className="flex h-screen bg-[#0F172A] text-slate-200 font-sans selection:bg-cyan-500/30 overflow-hidden relative">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />

      {/* Sidebar / Observability */}
      <div className="w-80 bg-slate-900/50 backdrop-blur-xl border-r border-white/10 flex flex-col z-10 shadow-2xl">
        <div className="p-6 border-b border-white/5 bg-gradient-to-br from-slate-800/40 to-slate-900/40">
          <h1 className="text-2xl font-bold flex items-center gap-3 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
            <Sparkles className="text-cyan-400 h-6 w-6" /> EquiTie
          </h1>
          <p className="text-xs text-slate-400 mt-2 font-medium tracking-wide uppercase">AI Portfolio Assistant</p>
        </div>

        <div className="p-6 border-b border-white/5 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />
          <label className="text-xs font-semibold mb-3 text-slate-400 flex items-center gap-2 uppercase tracking-wider relative z-10">
            <User className="h-3 w-3" /> Simulate Investor
          </label>
          <div className="relative z-10">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
            </div>
            <select
              className="w-full pl-8 pr-8 py-3 rounded-xl border border-white/10 bg-slate-800/80 text-white text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all appearance-none cursor-pointer shadow-inner"
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
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <ChevronRight className="h-4 w-4 text-slate-500 rotate-90" />
            </div>
          </div>
        </div>

        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar">
          <h2 className="text-xs font-bold mb-4 flex items-center gap-2 text-slate-400 uppercase tracking-wider">
            <Activity className="h-4 w-4 text-purple-400" /> Observability
          </h2>

          <div className="space-y-4">
            {/* Latency Card */}
            <div className="group bg-slate-800/40 hover:bg-slate-800/60 transition-colors p-4 rounded-2xl border border-white/5 hover:border-white/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                <Clock className="h-10 w-10 text-cyan-400" />
              </div>
              <div className="text-xs text-slate-400 mb-2 relative z-10">Network Latency</div>
              <div className="flex items-baseline gap-1 relative z-10">
                <span className="text-2xl font-light text-white">{latency}</span>
                <span className="text-sm font-medium text-slate-500">ms</span>
              </div>
            </div>

            {/* Token & Cost Card */}
            <div className="group bg-slate-800/40 hover:bg-slate-800/60 transition-colors p-4 rounded-2xl border border-white/5 hover:border-white/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                <Zap className="h-10 w-10 text-purple-400" />
              </div>
              <div className="text-xs text-slate-400 mb-3 relative z-10">Tokens & Inference Cost</div>

              <div className="space-y-2 relative z-10">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-400 flex items-center gap-1.5"><ChevronRight className="h-3 w-3" />Prompt</span>
                  <span className="font-mono text-cyan-300 bg-cyan-900/30 px-2 py-0.5 rounded text-xs">{usage.prompt}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-400 flex items-center gap-1.5"><ChevronRight className="h-3 w-3" />Completion</span>
                  <span className="font-mono text-purple-300 bg-purple-900/30 px-2 py-0.5 rounded text-xs">{usage.completion}</span>
                </div>
                <div className="pt-3 mt-1 border-t border-white/5 flex justify-between items-center">
                  <span className="text-xs font-medium text-slate-300">Est. Cost</span>
                  <span className="font-mono text-emerald-400 font-semibold">${cost.toFixed(6)}</span>
                </div>
              </div>
            </div>

            {/* Tool Calls Card */}
            <div className="bg-slate-800/40 p-4 rounded-2xl border border-white/5">
              <div className="flex items-center gap-2 mb-3">
                <Database className="h-4 w-4 text-blue-400" />
                <div className="text-xs text-slate-400">Agent Tool Citations</div>
              </div>

              {toolCalls.length === 0 ? (
                <div className="flex items-center justify-center py-4 bg-slate-900/50 rounded-xl border border-white/5 border-dashed">
                  <span className="text-xs text-slate-500 italic">No deterministic tools executed</span>
                </div>
              ) : (
                <ul className="space-y-2">
                  {toolCalls.map((tc, i) => (
                    <li key={i} className="bg-slate-900/80 border border-indigo-500/20 p-3 rounded-xl hover:border-indigo-500/50 transition-colors group">
                      <div className="flex items-center gap-2 font-mono text-[11px] text-indigo-400 font-semibold mb-1.5">
                        <BarChart3 className="h-3 w-3" /> {tc.function}()
                      </div>
                      <div className="font-mono text-[10px] text-slate-400 bg-black/40 p-2 rounded-lg break-all group-hover:text-slate-300 transition-colors border border-white/5">
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
      <div className="flex-1 flex flex-col relative z-10 bg-slate-900/30 backdrop-blur-md">
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="absolute top-6 right-8 p-2 px-3 bg-slate-800/80 hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-white/10 hover:border-red-500/30 rounded-xl transition-all shadow-sm z-50 flex items-center gap-2 text-xs font-semibold animate-fade-in"
            title="Reset Chat"
          >
            <Trash2 className="h-4 w-4" /> Reset Chat
          </button>
        )}

        {/* Messages */}
        <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 pt-24 md:p-10 md:pt-24 space-y-8 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-6 max-w-lg mx-auto text-center">
              <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 p-5 rounded-3xl border border-cyan-500/20 shadow-lg shadow-cyan-500/10 mb-4 animate-float">
                <Activity className="h-12 w-12 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">Welcome to EquiTie</h3>
                <p className="text-slate-400 leading-relaxed">
                  Select an investor from the sidebar and ask questions regarding their portfolio. The agent will retrieve live data using deterministic Python tools.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 w-full mt-4">
                <button
                  onClick={() => setInput("What is my current MOIC?")}
                  className="flex-1 py-3 px-4 bg-slate-800/80 border border-white/10 rounded-xl text-sm font-medium hover:bg-slate-700 hover:border-cyan-500/50 hover:text-white transition-all shadow-sm group"
                >
                  <span className="flex items-center justify-center gap-2">
                    What is my current MOIC? <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                  </span>
                </button>
                <button
                  onClick={() => setInput("Show me my upcoming capital calls.")}
                  className="flex-1 py-3 px-4 bg-slate-800/80 border border-white/10 rounded-xl text-sm font-medium hover:bg-slate-700 hover:border-purple-500/50 hover:text-white transition-all shadow-sm group"
                >
                  <span className="flex items-center justify-center gap-2">
                    Upcoming capital calls? <ChevronRight className="h-4 w-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                  </span>
                </button>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-8 w-full">
              {messages.filter(m => m.role === "user" || m.role === "assistant").map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}>
                  <div className={`max-w-3xl ${
                    msg.role === "user"
                      ? "bg-gradient-to-br from-cyan-600 to-blue-600 text-white rounded-2xl rounded-tr-sm shadow-lg shadow-cyan-900/20 px-6 py-4"
                      : "bg-slate-800/80 backdrop-blur-md border border-white/10 text-slate-200 rounded-2xl rounded-tl-sm shadow-xl px-6 py-5"
                  }`}>
                    {msg.role === "assistant" && (
                      <div className="flex items-center gap-2 mb-3 border-b border-white/5 pb-3">
                        <div className="bg-indigo-500/20 p-1.5 rounded-lg border border-indigo-500/30">
                          <Activity className="h-4 w-4 text-indigo-400" />
                        </div>
                        <span className="text-xs font-semibold text-slate-300 uppercase tracking-widest">EquiTie Agent</span>
                      </div>
                    )}
                    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-slate-900/80 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl">
                      <ReactMarkdown>
                        {msg.content || ""}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {isLoading && (
            <div className="max-w-4xl mx-auto w-full flex justify-start animate-fade-in">
              <div className="bg-slate-800/80 backdrop-blur-md border border-white/10 p-5 rounded-2xl rounded-tl-sm shadow-xl flex items-center gap-4">
                <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
                <span className="text-sm text-slate-400 font-medium animate-pulse">Agent is reasoning and querying data...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-slate-900/80 backdrop-blur-xl border-t border-white/10 relative z-20">
          <form onSubmit={handleSubmit} className="flex gap-4 max-w-4xl mx-auto relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={selectedInvestor ? (isListening ? "Listening..." : "Ask a question about the portfolio...") : "Select an investor first..."}
              className={`flex-1 px-6 py-4 pr-24 rounded-2xl border ${isListening ? "border-cyan-500/50 bg-cyan-900/20 text-cyan-50" : "border-white/10 bg-slate-800/90 text-white"} placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 shadow-inner text-base transition-all relative z-10`}
              disabled={isLoading || !selectedInvestor}
            />

            <div className="absolute right-2 top-2 bottom-2 flex gap-2 z-20">
              <button
                type="button"
                onClick={toggleListen}
                disabled={isLoading || !selectedInvestor || !isSpeechSupported}
                className={`aspect-square rounded-xl flex items-center justify-center transition-all shadow-md ${
                  isListening
                    ? "bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse hover:bg-red-500/30"
                    : "bg-slate-700/50 text-slate-300 border border-white/5 hover:bg-slate-700 hover:text-white disabled:opacity-50 disabled:grayscale"
                }`}
                title={isListening ? "Stop listening" : "Start voice input"}
              >
                {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>
              <button
                type="submit"
                disabled={isLoading || !selectedInvestor || !input.trim()}
                className="aspect-square bg-gradient-to-br from-cyan-500 to-blue-600 text-white rounded-xl flex items-center justify-center hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 disabled:grayscale transition-all shadow-lg"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </form>
          <div className="max-w-4xl mx-auto text-center mt-3">
            <span className="text-[10px] text-slate-500 font-medium uppercase tracking-widest">
              EquiTie AI can make mistakes. All outputs are generated for prototype validation only.
            </span>
          </div>
        </div>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: rgba(255, 255, 255, 0.2);
        }

        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
