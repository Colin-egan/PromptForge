"use client";

import { useState, useRef, useEffect } from "react";
import { sendChat, modelExportUrl, type ChatResponse, type Parameter } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  modelId?: string;
  intent?: string;
}

interface ChatPanelProps {
  onModelReady: (modelId: string, parameters?: Parameter[]) => void;
  onParametersUpdate: (parameters: Parameter[]) => void;
}

export default function ChatPanel({ onModelReady, onParametersUpdate }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm PromptForge. Describe any 3D-printable object and I'll generate it for you. Try: \"make me a phone holder\" or \"design a small desk organizer\".",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentModelId, setCurrentModelId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const resp: ChatResponse = await sendChat(text, currentModelId);

      if (resp.model_id) {
        setCurrentModelId(resp.model_id);
        onModelReady(resp.model_id, resp.parameters);
        
        // Update parameters if provided
        if (resp.parameters) {
          onParametersUpdate(resp.parameters);
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: resp.message,
          modelId: resp.model_id,
          intent: resp.intent,
        },
      ]);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Something went wrong: ${message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full" style={{ background: "var(--surface)", borderRight: "1px solid var(--border)" }}>
      {/* Header */}
      <div className="px-4 py-3 font-semibold text-sm tracking-wide" style={{ borderBottom: "1px solid var(--border)", color: "var(--accent)" }}>
        PromptForge
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className="rounded-xl px-4 py-2 max-w-xs text-sm leading-relaxed"
              style={{
                background: msg.role === "user" ? "var(--accent)" : "var(--bg)",
                color: "var(--text)",
              }}
            >
              {msg.content}
              {msg.modelId && (
                <div className="mt-2 flex gap-2 flex-wrap">
                  <a
                    href={modelExportUrl(msg.modelId, "stl")}
                    download
                    className="text-xs px-2 py-1 rounded"
                    style={{ background: "var(--surface)", color: "var(--muted)" }}
                  >
                    Download STL
                  </a>
                  <a
                    href={modelExportUrl(msg.modelId, "glb")}
                    download
                    className="text-xs px-2 py-1 rounded"
                    style={{ background: "var(--surface)", color: "var(--muted)" }}
                  >
                    Download GLB
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-xl px-4 py-2 text-sm" style={{ background: "var(--bg)", color: "var(--muted)" }}>
              Generating<span className="animate-pulse">...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3" style={{ borderTop: "1px solid var(--border)" }}>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg px-3 py-2 text-sm outline-none"
            style={{ background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)" }}
            placeholder="Describe your 3D model..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-lg px-4 py-2 text-sm font-medium disabled:opacity-40"
            style={{ background: "var(--accent)", color: "#fff" }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
