"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Agent } from "@/lib/types";
import { fetchAgent } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

/**
 * Agent Detail Page — Full metadata view for a single agent.
 */
export default function AgentDetailPage() {
  const params = useParams();
  const agentId = params.id as string;

  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!agentId) return;
    fetchAgent(agentId)
      .then(setAgent)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [agentId]);

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  const parseTools = (toolsStr: string): string[] => {
    try {
      return JSON.parse(toolsStr);
    } catch {
      return [];
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="skeleton" style={{ width: 120, height: 16, marginBottom: 24 }} />
        <div className="skeleton" style={{ width: 280, height: 32, marginBottom: 12 }} />
        <div className="skeleton" style={{ width: 200, height: 16, marginBottom: 32 }} />
        <div className="skeleton" style={{ height: 300, borderRadius: "var(--radius-lg)" }} />
      </div>
    );
  }

  // Error state
  if (error || !agent) {
    return (
      <div className="animate-fade-in">
        <Link
          href="/agents"
          style={{
            fontSize: "13px",
            color: "var(--text-secondary)",
            textDecoration: "none",
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            marginBottom: "24px",
          }}
        >
          ← Back to Agents
        </Link>
        <div className="card" style={{ padding: "60px 40px", textAlign: "center" }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--accent-red)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 14 }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 6px" }}>
            Agent not found
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
            {error || `No agent found with ID: ${agentId}`}
          </p>
        </div>
      </div>
    );
  }

  const tools = parseTools(agent.tools);

  return (
    <div className="animate-fade-in">
      {/* Breadcrumb */}
      <Link
        href="/agents"
        style={{
          fontSize: "13px",
          color: "var(--text-secondary)",
          textDecoration: "none",
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          marginBottom: "20px",
          transition: "color var(--transition-fast)",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-accent)")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}
      >
        ← Back to Agents
      </Link>

      {/* Agent Header */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: "16px",
          marginBottom: "32px",
        }}
      >
        {/* Agent avatar */}
        <div
          style={{
            width: 52,
            height: 52,
            borderRadius: "var(--radius-md)",
            background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-emerald))",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 800,
            fontSize: "18px",
            color: "hsl(220, 20%, 6%)",
            flexShrink: 0,
          }}
        >
          {agent.name.slice(0, 2).toUpperCase()}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
            <h1
              style={{
                fontSize: "24px",
                fontWeight: 700,
                color: "var(--text-primary)",
                letterSpacing: "-0.02em",
                margin: 0,
              }}
            >
              {agent.name}
            </h1>
            <StatusBadge status={agent.status} />
            <span
              style={{
                fontSize: "12px",
                fontFamily: "var(--font-mono)",
                color: "var(--text-tertiary)",
                background: "var(--bg-tertiary)",
                padding: "3px 8px",
                borderRadius: "4px",
              }}
            >
              v{agent.version}
            </span>
          </div>
          <p
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
              marginTop: "6px",
            }}
          >
            {agent.description || "No description provided."}
          </p>
        </div>
      </div>

      {/* Detail Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {/* Configuration Card */}
        <div className="card" style={{ padding: "22px 24px" }}>
          <h3
            style={{
              fontSize: "12px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "var(--text-tertiary)",
              marginBottom: "16px",
              margin: "0 0 16px",
            }}
          >
            Configuration
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <DetailRow label="Model" value={agent.model} mono />
            <DetailRow label="Temperature" value={String(agent.temperature)} />
            <DetailRow label="Agent ID" value={agent.id} mono small />
          </div>
        </div>

        {/* Tools Card */}
        <div className="card" style={{ padding: "22px 24px" }}>
          <h3
            style={{
              fontSize: "12px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "var(--text-tertiary)",
              margin: "0 0 16px",
            }}
          >
            Tools ({tools.length})
          </h3>
          {tools.length > 0 ? (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {tools.map((tool) => (
                <span
                  key={tool}
                  style={{
                    padding: "5px 12px",
                    background: "var(--bg-tertiary)",
                    border: "1px solid var(--border-primary)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "12px",
                    fontFamily: "var(--font-mono)",
                    color: "var(--text-secondary)",
                  }}
                >
                  {tool}
                </span>
              ))}
            </div>
          ) : (
            <p
              style={{
                fontSize: "13px",
                color: "var(--text-tertiary)",
                margin: 0,
                fontStyle: "italic",
              }}
            >
              No tools assigned
            </p>
          )}
        </div>

        {/* Timestamps Card */}
        <div className="card" style={{ padding: "22px 24px" }}>
          <h3
            style={{
              fontSize: "12px",
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "var(--text-tertiary)",
              margin: "0 0 16px",
            }}
          >
            Timestamps
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <DetailRow label="Created" value={formatDate(agent.created_at)} />
            <DetailRow label="Last Updated" value={formatDate(agent.updated_at)} />
          </div>
        </div>
      </div>

      {/* System Prompt */}
      <div className="card" style={{ padding: "22px 24px" }}>
        <h3
          style={{
            fontSize: "12px",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            color: "var(--text-tertiary)",
            margin: "0 0 14px",
          }}
        >
          System Prompt
        </h3>
        <pre
          style={{
            background: "var(--bg-primary)",
            border: "1px solid var(--border-primary)",
            borderRadius: "var(--radius-sm)",
            padding: "16px 18px",
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            color: "var(--text-secondary)",
            lineHeight: 1.6,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            margin: 0,
            overflow: "auto",
            maxHeight: "300px",
          }}
        >
          {agent.system_prompt}
        </pre>
      </div>
    </div>
  );
}

/**
 * A single key-value detail row.
 */
function DetailRow({
  label,
  value,
  mono,
  small,
}: {
  label: string;
  value: string;
  mono?: boolean;
  small?: boolean;
}) {
  return (
    <div>
      <div
        style={{
          fontSize: "11px",
          fontWeight: 500,
          color: "var(--text-tertiary)",
          marginBottom: "3px",
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: small ? "12px" : "14px",
          fontWeight: 500,
          color: "var(--text-primary)",
          fontFamily: mono ? "var(--font-mono)" : "inherit",
          wordBreak: "break-all",
        }}
      >
        {value}
      </div>
    </div>
  );
}
