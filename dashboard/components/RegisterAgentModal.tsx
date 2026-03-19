"use client";

import { useState } from "react";
import { registerAgent } from "@/lib/api";

interface RegisterAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function RegisterAgentModal({ isOpen, onClose, onSuccess }: RegisterAgentModalProps) {
  const [name, setName] = useState("");
  const [model, setModel] = useState("gpt-4o");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await registerAgent({
        name,
        model,
        system_prompt: systemPrompt,
        temperature,
        version: "1.0.0",
        status: "active",
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to register agent");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1100,
        backdropFilter: "blur(4px)",
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "var(--bg-secondary)",
          border: "1px solid var(--border-subtle)",
          borderRadius: "16px",
          width: "100%",
          maxWidth: "500px",
          padding: "32px",
          boxShadow: "0 20px 40px rgba(0, 0, 0, 0.4)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ fontSize: "22px", fontWeight: 700, marginBottom: "8px" }}>Register New Agent</h2>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "24px" }}>
          Define the identity and model for your new autonomous agent.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", fontSize: "12px", color: "var(--text-tertiary)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Agent Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. ResearchBot"
              required
              style={{ width: "100%", padding: "12px", borderRadius: "10px", background: "var(--bg-primary)", border: "1px solid var(--border-subtle)", outline: "none" }}
            />
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", fontSize: "12px", color: "var(--text-tertiary)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>LLM Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              style={{ width: "100%", padding: "12px", borderRadius: "10px", background: "var(--bg-primary)", border: "1px solid var(--border-subtle)", outline: "none" }}
            >
              <option value="gpt-4o">GPT-4o (OpenAI)</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="claude-3-opus-20240229">Claude 3 Opus</option>
              <option value="llama3-70b-8192">Llama 3 (Groq)</option>
            </select>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", fontSize: "12px", color: "var(--text-tertiary)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>System Prompt</label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="You are a helpful assistant..."
              rows={4}
              required
              style={{ width: "100%", padding: "12px", borderRadius: "10px", background: "var(--bg-primary)", border: "1px solid var(--border-subtle)", outline: "none", resize: "none" }}
            />
          </div>

          {error && <p style={{ color: "var(--accent-red)", fontSize: "14px", marginBottom: "16px" }}>{error}</p>}

          <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
            <button
              type="button"
              onClick={onClose}
              style={{ flex: 1, padding: "12px", borderRadius: "10px", border: "1px solid var(--border-subtle)", background: "transparent", color: "var(--text-primary)", cursor: "pointer" }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{ flex: 2, padding: "12px", borderRadius: "10px", background: "var(--accent-cyan)", color: "var(--bg-primary)", fontWeight: 600, border: "none", cursor: loading ? "not-allowed" : "pointer" }}
            >
              {loading ? "Registering..." : "Complete Registration"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
