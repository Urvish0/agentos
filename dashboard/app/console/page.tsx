"use client";

import React, { useState, useEffect } from "react";
import Terminal from "@/components/terminal/Terminal";
import { fetchAgents, fetchTasks } from "@/lib/api";
import { Agent, Task } from "@/lib/types";

export default function ConsolePage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState("");
  const [tasks, setTasks] = useState<any[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState("");
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("gpt-4o");
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);
  
  // New Model Form State
  const [newModelName, setNewModelName] = useState("");
  const [newModelId, setNewModelId] = useState("");
  const [newModelProvider, setNewModelProvider] = useState("openai");
  const [newModelApiKey, setNewModelApiKey] = useState("");
  const [newModelBaseUrl, setNewModelBaseUrl] = useState("");

  const [logs, setLogs] = useState<string[]>([
    "[INFO] Agent Command Center Initialized",
    "[INFO] Ready to attach to live sessions..."
  ]);
  const [streaming, setStreaming] = useState(false);
  const [inputText, setInputText] = useState("");

  useEffect(() => {
    // Fetch Agents
    fetch("/api/agents")
      .then(res => res.json())
      .then(data => {
        setAgents(data);
        if (data.length > 0) setSelectedAgentId(data[0].id);
      })
      .catch(console.error);

    // Fetch Recent Tasks
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => {
        setTasks(data.slice(0, 10));
        if (data.length > 0) setSelectedTaskId(data[0].id);
      })
      .catch(console.error);

    // Fetch Available Models
    fetch("/api/console/models")
      .then(res => res.json())
      .then(data => setModels(data))
      .catch(console.error);
  }, []);

  // SSE Stream Management
  useEffect(() => {
    let eventSource: EventSource | null = null;

    if (streaming && selectedTaskId) {
      const url = `/api/tasks/${selectedTaskId}/logs/stream`;
      eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.status) {
            setLogs(prev => [...prev, `[STATUS] Task is now ${data.status.toUpperCase()}`]);
            // Refresh task list when status changes to completed/failed
            if (["completed", "failed", "cancelled"].includes(data.status)) {
              refreshTaskList();
            }
          }
          if (data.output) {
            setLogs(prev => [...prev, `[OUTPUT] ${data.output}`]);
          }
          if (data.error) {
            setLogs(prev => [...prev, `[ERROR] ${data.error}`]);
          }
          if (data.info === "Session terminated") {
            setLogs(prev => [...prev, "[INFO] SSE Session Terminated."]);
            setStreaming(false);
            eventSource?.close();
          }
        } catch (e) {
          console.error("Failed to parse SSE data", e);
        }
      };

      eventSource.onerror = () => {
        // Only log error if the stream wasn't intentionally closed
        if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
          setLogs(prev => [...prev, "[WARN] Log stream connection interrupted. Reconnecting..."]);
        }
        setStreaming(false);
        eventSource?.close();
      };
    }

    return () => {
      eventSource?.close();
    };
  }, [streaming, selectedTaskId]);

  // Helper to refresh task list
  const refreshTaskList = () => {
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => setTasks(data.slice(0, 10)))
      .catch(console.error);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !selectedAgentId) return;

    const msg = inputText;
    setInputText("");
    setLogs(prev => [...prev, `[USER] ${msg}`]);

    try {
      const res = await fetch("/api/console/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          agent_id: selectedAgentId, 
          message: msg,
          model: selectedModel 
        })
      });
      
      if (!res.ok) throw new Error("Failed to send message");
      
      const data = await res.json();
      setLogs(prev => [...prev, `[SYSTEM] Task created: ${data.task_id.slice(0, 8)}. Using model: ${selectedModel}`]);
      
      // Auto-attach to the new task logs
      setSelectedTaskId(data.task_id);
      setStreaming(true);

      // Refresh task list to show new task in Session History
      setTimeout(refreshTaskList, 500);

    } catch (err: any) {
      setLogs(prev => [...prev, `[ERROR] ${err.message}`]);
    }
  };

  const handleAddCustomModel = async () => {
    const payload = {
      name: newModelName,
      model_id: newModelId,
      provider: newModelProvider,
      api_key: newModelApiKey || null,
      base_url: newModelBaseUrl || null
    };

    try {
      const res = await fetch("/api/console/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to add model");
      
      // Refresh models
      const data = await res.json();
      setModels(prev => [...prev, { ...data, is_custom: true }]);
      setIsModelModalOpen(false);
      setLogs(prev => [...prev, `[SYSTEM] Registered custom model: ${data.name}`]);
    } catch (err: any) {
      alert("Error adding model: " + err.message);
    }
  };

  const handleExecuteCommand = async (command: string) => {
    if (!selectedAgentId) return;
    setLogs(prev => [...prev, `[SYSTEM] Running command: ${command}...`]);
    
    try {
      const res = await fetch("/api/console/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: selectedAgentId, command })
      });
      const data = await res.json();
      setLogs(prev => [...prev, `[INFO] ${data.details}`]);
    } catch (err: any) {
      setLogs(prev => [...prev, `[ERROR] ${err.message}`]);
    }
  };

  const toggleStreaming = () => {
    if (!selectedTaskId && !streaming) {
      setLogs(prev => [...prev, "[WARN] Select a task to attach the stream."]);
      return;
    }
    setStreaming(!streaming);
    if (!streaming) {
      setLogs(prev => [...prev, `[INFO] Connecting to log stream for task ${selectedTaskId.slice(0, 8)}...`]);
    } else {
      setLogs(prev => [...prev, "[INFO] Log stream disconnected."]);
    }
  };

  return (
    <div className="animate-fade-in" style={{ height: "calc(100vh - 100px)", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <header style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.03em", margin: "0 0 6px" }}>
          Agent Command Center
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
          Interactive shell and real-time log streaming for deep debugging.
        </p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: "24px", flex: 1, minHeight: 0 }}>
        {/* Main Terminal Area */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px", minHeight: 0 }}>
          <Terminal logs={logs} loading={streaming} height="100%" />

          {/* Input Bar */}
          <form onSubmit={handleSendMessage} style={{ display: "flex", gap: "12px", background: "var(--bg-tertiary)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-primary)" }}>
            <div style={{ color: "var(--accent-cyan)", display: "flex", alignItems: "center", fontWeight: 700, fontSize: "18px", paddingLeft: "8px" }}>❯</div>
            <input 
              type="text" 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={selectedAgentId ? `Send command to agent ${selectedAgentId.slice(0, 8)}...` : "Select an agent to begin..."}
              style={{ flex: 1, background: "transparent", border: "none", color: "var(--text-primary)", outline: "none", fontSize: "14px", fontFamily: "var(--font-mono)" }}
            />
            <button 
              type="submit"
              disabled={!inputText.trim() || !selectedAgentId}
              style={{ padding: "6px 16px", background: "var(--accent-cyan)", color: "black", border: "none", borderRadius: "var(--radius-sm)", fontWeight: 700, fontSize: "12px", cursor: inputText.trim() ? "pointer" : "default", opacity: inputText.trim() ? 1 : 0.5 }}
            >
              RUN
            </button>
          </form>
        </div>

        {/* Control Panel Sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Session Controls */}
          <section className="card" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-tertiary)", marginBottom: "16px", letterSpacing: "0.05em" }}>Session Controls</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <label style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase" }}>Target Agent</label>
                <select
                  value={selectedAgentId}
                  onChange={(e) => setSelectedAgentId(e.target.value)}
                  className="select-custom"
                >
                  {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                </select>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <label style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase" }}>Active Model</label>
                <div style={{ display: "flex", gap: "8px" }}>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="select-custom"
                    style={{ flex: 1 }}
                  >
                    {models.map(m => (
                      <option key={m.id} value={m.name}>
                        {m.name} {m.is_custom ? "⭐" : ""}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setIsModelModalOpen(true)}
                    className="btn-shell"
                    style={{ padding: "0 12px", width: "40px", textAlign: "center" }}
                    title="Register Custom Model"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Session History */}
          <section className="card" style={{ padding: "16px", flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
            <h3 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-tertiary)", marginBottom: "12px", letterSpacing: "0.05em" }}>Session History</h3>
            <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "8px", paddingRight: "4px" }}>
              {tasks.length === 0 ? (
                <p style={{ fontSize: "12px", color: "var(--text-tertiary)", textAlign: "center", padding: "20px" }}>No recent tasks</p>
              ) : (
                tasks.map(t => (
                  <div
                    key={t.id}
                    onClick={() => {
                      setSelectedTaskId(t.id);
                      setStreaming(true);
                      setLogs(prev => [...prev, `[INFO] Re-attaching to session ${t.id.slice(0,8)}...`]);
                    }}
                    style={{
                      padding: "10px",
                      borderRadius: "8px",
                      background: selectedTaskId === t.id ? "var(--bg-tertiary)" : "transparent",
                      border: "1px solid",
                      borderColor: selectedTaskId === t.id ? "var(--accent-cyan)" : "var(--border-subtle)",
                      cursor: "pointer",
                      transition: "all 0.2s"
                    }}
                    onMouseEnter={(e) => {
                      if (selectedTaskId !== t.id) e.currentTarget.style.borderColor = "var(--text-tertiary)";
                    }}
                    onMouseLeave={(e) => {
                      if (selectedTaskId !== t.id) e.currentTarget.style.borderColor = "var(--border-subtle)";
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                      <span style={{
                        fontSize: "10px",
                        fontWeight: 700,
                        color: t.status === "completed" ? "var(--accent-green)" : t.status === "failed" ? "var(--accent-red)" : "var(--accent-cyan)",
                        textTransform: "uppercase"
                      }}>
                        {t.status}
                      </span>
                      <span style={{ fontSize: "10px", color: "var(--text-tertiary)" }}>
                        {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div style={{
                      fontSize: "12px",
                      color: "var(--text-primary)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      fontFamily: "var(--font-mono)"
                    }}>
                      {t.input}
                    </div>
                  </div>
                ))
              )}
            </div>
            <button
              onClick={toggleStreaming}
              className={`btn-primary ${streaming ? 'streaming-active' : ''}`}
              style={{ width: "100%", marginTop: "16px" }}
            >
              {streaming ? "Detach Stream" : "Attach Log Stream"}
            </button>
          </section>

          {/* Quick Shell Commands */}
          <section className="card" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-tertiary)", marginBottom: "16px", letterSpacing: "0.05em" }}>Quick Shell Commands</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <button onClick={() => handleExecuteCommand('inspect_memory')} className="btn-shell">
                Inspect Memory
              </button>
              <button onClick={() => handleExecuteCommand('clear_context')} className="btn-shell">
                Clear Context
              </button>
              <button onClick={() => setLogs([])} className="btn-shell">
                Clear Console
              </button>
            </div>
          </section>
        </div>
      </div>

      {/* Custom Model Modal */}
      {isModelModalOpen && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.85)", backdropFilter: "blur(8px)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
          padding: "20px"
        }}>
          <div className="card" style={{ width: "100%", maxWidth: "480px", padding: "32px", border: "1px solid var(--border-color)" }}>
            <h2 style={{ fontSize: "20px", fontWeight: 600, marginBottom: "8px" }}>Register Custom Model</h2>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "24px" }}>
              Add support for open-source models (Ollama/LLaMA) or your own API endpoints.
            </p>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-tertiary)" }}>Model Display Name</label>
                <input 
                  type="text" value={newModelName} onChange={(e) => setNewModelName(e.target.value)}
                  placeholder="e.g. My LLaMA 3" className="select-custom" style={{ background: "var(--bg-primary)" }}
                />
              </div>

              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-tertiary)" }}>Model Identifier</label>
                <input 
                  type="text" value={newModelId} onChange={(e) => setNewModelId(e.target.value)}
                  placeholder="e.g. llama3, mixtral-8x7b" className="select-custom" style={{ background: "var(--bg-primary)" }}
                />
              </div>

              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-tertiary)" }}>Provider</label>
                <select 
                  value={newModelProvider} onChange={(e) => setNewModelProvider(e.target.value)}
                  className="select-custom" style={{ background: "var(--bg-primary)" }}
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="groq">Groq</option>
                  <option value="ollama">Ollama (Local)</option>
                </select>
              </div>

              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-tertiary)" }}>API Key (Optional)</label>
                <input 
                  type="password" value={newModelApiKey} onChange={(e) => setNewModelApiKey(e.target.value)}
                  placeholder="sk-..." className="select-custom" style={{ background: "var(--bg-primary)" }}
                />
              </div>

              <div className="form-group" style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-tertiary)" }}>Base URL (For Ollama/Custom)</label>
                <input 
                  type="text" value={newModelBaseUrl} onChange={(e) => setNewModelBaseUrl(e.target.value)}
                  placeholder="http://localhost:11434" className="select-custom" style={{ background: "var(--bg-primary)" }}
                />
              </div>
            </div>

            <div style={{ display: "flex", gap: "12px", marginTop: "32px" }}>
              <button 
                onClick={() => setIsModelModalOpen(false)}
                className="btn-shell" style={{ flex: 1, textAlign: "center" }}
              >
                Cancel
              </button>
              <button 
                onClick={handleAddCustomModel}
                className="btn-primary" style={{ flex: 2 }}
              >
                Register Model
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .select-custom {
          width: 100%;
          background: var(--bg-tertiary);
          border: 1px solid var(--border-primary);
          color: var(--text-primary);
          padding: 10px 12px;
          border-radius: var(--radius-sm);
          font-size: 13px;
          outline: none;
          transition: all 0.2s;
        }
        .select-custom:focus {
          border-color: var(--accent-cyan);
        }
        .btn-shell {
          width: 100%;
          padding: 8px 12px;
          text-align: left;
          background: transparent;
          border: 1px solid var(--border-primary);
          color: var(--text-secondary);
          border-radius: var(--radius-sm);
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .btn-shell:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
          border-color: var(--accent-cyan);
        }
        .btn-primary.streaming-active {
          background: hsl(0, 50%, 25%);
          border-color: hsl(0, 50%, 40%);
          color: white;
        }
      `}</style>
    </div>
  );
}

