"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Bot, User as UserIcon, Loader2, MessageSquare, FileText, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import api from "@/services/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: { content: string; metadata: Record<string, unknown> }[];
}

interface Document {
  id: number;
  file_name: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get("/documents/");
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDocuments();
  }, [fetchDocuments]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const payload: Record<string, unknown> = { query: userMsg.content };
      if (selectedDocIds.length > 0) {
        payload.document_ids = selectedDocIds;
      }

      const token = localStorage.getItem('access_token');
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      
      const res = await fetch(`${baseUrl}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
          return;
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      if (!res.body) {
        throw new Error("No response body");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      const botMsgId = (Date.now() + 1).toString();
      
      setMessages((prev) => [...prev, { id: botMsgId, role: "assistant", content: "", sources: [] }]);
      setIsLoading(false);

      let done = false;
      let textBuffer = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          textBuffer += decoder.decode(value, { stream: true });
          const lines = textBuffer.split('\n');
          textBuffer = lines.pop() || "";
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6);
              if (dataStr.trim() === '[DONE]') {
                done = true;
                break;
              }
              try {
                const data = JSON.parse(dataStr);
                setMessages((prev) => 
                  prev.map((msg) => {
                    if (msg.id === botMsgId) {
                      return {
                        ...msg,
                        content: data.chunk ? msg.content + data.chunk : (data.error ? msg.content + "\n\nError: " + data.error : msg.content),
                        sources: data.sources ? data.sources : msg.sources
                      };
                    }
                    return msg;
                  })
                );
              } catch (e) {
                console.error("Error parsing stream data:", e);
              }
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setIsLoading(false);
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: "assistant", content: "Sorry, I encountered an error. Make sure documents are uploaded and Ollama is running locally." },
      ]);
    }
  };

  return (
    <div className="h-full flex flex-col bg-zinc-900/30 border border-zinc-800/50 rounded-3xl overflow-hidden backdrop-blur-xl">
      {/* Header */}
      <div className="p-6 border-b border-zinc-800/50 bg-zinc-900/80">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          Smart Document Assistant
        </h1>
        <p className="text-sm text-zinc-400 mt-1">Ask questions about your uploaded documents.</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-500 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-zinc-800/50 flex items-center justify-center">
              <MessageSquare className="w-8 h-8 text-zinc-400" />
            </div>
            <p className="text-center max-w-sm">
              Hello! I&apos;m ready to answer questions based on your documents. Try asking something specific.
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 max-w-[85%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : ""}`}
              >
                <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center mt-1 ${
                  msg.role === "user" ? "bg-indigo-500 text-white" : "bg-zinc-800 text-cyan-400"
                }`}>
                  {msg.role === "user" ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                
                <div className={`space-y-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`p-4 rounded-2xl ${
                    msg.role === "user" 
                      ? "bg-indigo-600 text-white rounded-tr-sm" 
                      : "bg-zinc-800/80 text-zinc-200 rounded-tl-sm border border-zinc-700/50"
                  }`}>
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                  </div>
                  
                  {/* Sources display */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 space-y-2">
                      <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Sources</p>
                      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                        {msg.sources.slice(0, 3).map((source, idx) => (
                          <div key={idx} className="shrink-0 w-64 p-3 rounded-xl bg-zinc-900/50 border border-zinc-800 text-xs">
                            <p className="font-medium text-indigo-400 mb-1 truncate" title={source.metadata.source as string}>
                              {(source.metadata.source as string) || "Document"}
                            </p>
                            <p className="text-zinc-400 line-clamp-3 leading-snug">{source.content}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
        
        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-[85%]">
             <div className="w-8 h-8 shrink-0 rounded-full bg-zinc-800 flex items-center justify-center text-cyan-400 mt-1">
               <Bot className="w-4 h-4" />
             </div>
             <div className="p-4 rounded-2xl bg-zinc-800/80 rounded-tl-sm border border-zinc-700/50 flex items-center gap-3">
               <Loader2 className="w-4 h-4 animate-spin text-zinc-400" />
               <span className="text-sm text-zinc-400">Analyzing documents...</span>
             </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-zinc-900/80 border-t border-zinc-800/50 flex flex-col gap-3">
        {documents.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
            {documents.map(doc => {
              const isSelected = selectedDocIds.includes(doc.id);
              return (
                <button
                  key={doc.id}
                  onClick={() => {
                    setSelectedDocIds(prev => 
                      isSelected ? prev.filter(id => id !== doc.id) : [...prev, doc.id]
                    );
                  }}
                  className={`shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors border ${
                    isSelected 
                      ? "bg-indigo-500/20 text-indigo-400 border-indigo-500/50" 
                      : "bg-zinc-800/50 text-zinc-400 border-zinc-700/50 hover:bg-zinc-800"
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[150px]">{doc.file_name}</span>
                  {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                </button>
              );
            })}
          </div>
        )}
        <form onSubmit={sendMessage} className="relative max-w-4xl mx-auto w-full">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your documents..."
            className="w-full bg-zinc-950 border border-zinc-800 rounded-full pl-6 pr-14 py-4 text-sm outline-none transition-all focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white disabled:opacity-50 disabled:bg-zinc-800 disabled:text-zinc-500 transition-all hover:bg-indigo-500 hover:scale-105 active:scale-95"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
