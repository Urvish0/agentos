"use client";

import React, { useEffect, useRef } from "react";

interface TerminalProps {
  logs: string[];
  title?: string;
  height?: string | number;
  loading?: boolean;
}

/**
 * Terminal — A high-fidelity console component for real-time log streaming.
 * Features auto-scrolling, monospaced typography, and dark-mode styling.
 */
export default function Terminal({ logs, title = "Agent Console", height = "400px", loading = false }: TerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new logs
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div 
      className="card" 
      style={{ 
        height, 
        padding: 0, 
        display: "flex", 
        flexDirection: "column", 
        background: "hsl(220, 20%, 6%)", 
        border: "1px solid var(--border-primary)", 
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
        boxShadow: "0 20px 50px rgba(0,0,0,0.5)"
      }}
    >
      {/* Terminal Header */}
      <div 
        style={{ 
          padding: "10px 16px", 
          background: "hsl(220, 20%, 10%)", 
          borderBottom: "1px solid var(--border-primary)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ display: "flex", gap: "6px" }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ff5f56" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ffbd2e" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#27c93f" }} />
          </div>
          <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.05em", fontFamily: "var(--font-mono)" }}>
            {title}
          </span>
        </div>
        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <div className="pulse-dot pulse-dot-active" style={{ width: 6, height: 6 }} />
            <span style={{ fontSize: "10px", color: "var(--text-tertiary)", fontWeight: 600 }}>Streaming...</span>
          </div>
        )}
      </div>

      {/* Terminal Body */}
      <div 
        ref={scrollRef}
        style={{ 
          flex: 1, 
          padding: "16px", 
          overflowY: "auto", 
          fontFamily: "var(--font-mono)", 
          fontSize: "13px", 
          lineHeight: "1.6", 
          color: "#e0e0e0",
          scrollBehavior: "smooth"
        }}
      >
        {logs.length === 0 ? (
          <div style={{ color: "var(--text-tertiary)", fontStyle: "italic" }}>
            {loading ? "Waiting for logs..." : "No logs available for this session."}
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} style={{ marginBottom: "2px", whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
              <span style={{ color: "var(--accent-cyan)", marginRight: "8px", opacity: 0.7 }}>❯</span>
              {parseLogLine(log)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/**
 * Simple parser to colorized log lines based on keywords
 */
function parseLogLine(line: string) {
  if (line.startsWith("[ERROR]") || line.includes("failed") || line.includes("Exception")) {
    return <span style={{ color: "#ff6b6b" }}>{line}</span>;
  }
  if (line.startsWith("[OUTPUT]")) {
    return <span style={{ color: "#e0e0e0", fontWeight: 400 }}>{line}</span>;
  }
  if (line.startsWith("[USER]")) {
    return <span style={{ color: "var(--accent-cyan)", fontWeight: 600 }}>{line}</span>;
  }
  if (line.startsWith("[SYSTEM]")) {
    return <span style={{ color: "#c084fc" }}>{line}</span>;
  }
  if (line.startsWith("[STATUS]")) {
    return <span style={{ color: "#ffd43b" }}>{line}</span>;
  }
  if (line.startsWith("[INFO]") || line.includes("success")) {
    return <span style={{ color: "var(--accent-emerald)" }}>{line}</span>;
  }
  if (line.startsWith("[WARN]")) {
    return <span style={{ color: "#ffd43b" }}>{line}</span>;
  }
  if (line.includes("Task:") || line.includes("Agent:")) {
    return <span style={{ color: "var(--accent-cyan)", fontWeight: 600 }}>{line}</span>;
  }
  return line;
}
