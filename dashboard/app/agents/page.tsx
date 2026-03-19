"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Agent } from "@/lib/types";
import { fetchAgents } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";
import RegisterAgentModal from "@/components/RegisterAgentModal";

/**
 * Agent List Page — Displays all registered agents with search/filter.
 */
export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);

  const loadAgents = () => {
    setLoading(true);
    fetchAgents()
      .then(setAgents)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const filteredAgents = agents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.model.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "28px",
          flexWrap: "wrap",
          gap: "16px",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "26px",
              fontWeight: 700,
              color: "var(--text-primary)",
              letterSpacing: "-0.02em",
              margin: 0,
            }}
          >
            Agents
          </h1>
          <p
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
              marginTop: "6px",
            }}
          >
            {loading
              ? "Loading agents..."
              : `${agents.length} agent${agents.length !== 1 ? "s" : ""} registered`}
          </p>
        </div>
        <button
          onClick={() => setIsRegisterModalOpen(true)}
          style={{
            padding: "10px 18px",
            background: "var(--accent-cyan)",
            color: "var(--bg-primary)",
            border: "none",
            borderRadius: "var(--radius-md)",
            fontSize: "14px",
            fontWeight: 600,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "opacity var(--transition-fast)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.9")}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Register Agent
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ position: "relative", maxWidth: "400px" }}>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--text-tertiary)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              position: "absolute",
              left: "14px",
              top: "50%",
              transform: "translateY(-50%)",
            }}
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search agents by name, description, or model..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 14px 10px 40px",
              background: "var(--bg-secondary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-primary)",
              fontSize: "13px",
              outline: "none",
              transition: "border-color var(--transition-fast)",
              fontFamily: "inherit",
            }}
            onFocus={(e) =>
              (e.currentTarget.style.borderColor = "var(--accent-cyan)")
            }
            onBlur={(e) =>
              (e.currentTarget.style.borderColor = "var(--border-primary)")
            }
          />
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
          }}
          className="card"
        >
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent-red)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ marginBottom: "14px" }}
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3
            style={{
              fontSize: "15px",
              fontWeight: 600,
              color: "var(--text-primary)",
              margin: "0 0 6px",
            }}
          >
            Cannot reach backend
          </h3>
          <p
            style={{
              fontSize: "13px",
              color: "var(--text-secondary)",
              margin: 0,
            }}
          >
            Make sure the AgentOS server is running on{" "}
            <code
              style={{
                fontFamily: "var(--font-mono)",
                background: "var(--bg-tertiary)",
                padding: "2px 6px",
                borderRadius: "4px",
              }}
            >
              localhost:8000
            </code>
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && !error && (
        <div className="stagger-children" style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: "64px", borderRadius: "var(--radius-md)" }}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && agents.length === 0 && (
        <div
          className="card"
          style={{
            padding: "60px 40px",
            textAlign: "center",
          }}
        >
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--text-tertiary)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ marginBottom: "16px", opacity: 0.6 }}
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
          </svg>
          <h3
            style={{
              fontSize: "17px",
              fontWeight: 600,
              color: "var(--text-primary)",
              margin: "0 0 8px",
            }}
          >
            No agents registered
          </h3>
          <p
            style={{
              fontSize: "13px",
              color: "var(--text-secondary)",
              margin: "0 0 20px",
              maxWidth: "380px",
              marginInline: "auto",
            }}
          >
            Register your first agent using the CLI:
          </p>
          <code
            style={{
              display: "inline-block",
              padding: "10px 18px",
              background: "var(--bg-tertiary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-sm)",
              fontFamily: "var(--font-mono)",
              fontSize: "13px",
              color: "var(--text-accent)",
            }}
          >
            agentos agents register agent.yaml
          </code>
        </div>
      )}

      {/* No Search Results */}
      {!loading && !error && agents.length > 0 && filteredAgents.length === 0 && (
        <div
          className="card"
          style={{ padding: "40px", textAlign: "center" }}
        >
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            No agents match &ldquo;<strong>{searchQuery}</strong>&rdquo;
          </p>
        </div>
      )}

      {/* Agent Table */}
      {!loading && !error && filteredAgents.length > 0 && (
        <div
          className="card"
          style={{ overflow: "hidden" }}
        >
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "1px solid var(--border-primary)",
                }}
              >
                {["Name", "Model", "Version", "Status", "Created"].map(
                  (header) => (
                    <th
                      key={header}
                      style={{
                        padding: "12px 18px",
                        textAlign: "left",
                        fontSize: "11px",
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                        color: "var(--text-tertiary)",
                      }}
                    >
                      {header}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody className="stagger-children">
              {filteredAgents.map((agent) => (
                <tr
                  key={agent.id}
                  style={{
                    borderBottom: "1px solid var(--border-primary)",
                    cursor: "pointer",
                    transition: "background var(--transition-fast)",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = "var(--bg-hover)")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = "transparent")
                  }
                >
                  <td style={{ padding: "14px 18px" }}>
                    <Link
                      href={`/agents/${agent.id}`}
                      style={{
                        textDecoration: "none",
                        display: "block",
                      }}
                    >
                      <div
                        style={{
                          fontSize: "14px",
                          fontWeight: 600,
                          color: "var(--text-primary)",
                          marginBottom: "2px",
                        }}
                      >
                        {agent.name}
                      </div>
                      <div
                        style={{
                          fontSize: "12px",
                          color: "var(--text-secondary)",
                          maxWidth: "300px",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {agent.description || "No description"}
                      </div>
                    </Link>
                  </td>
                  <td style={{ padding: "14px 18px" }}>
                    <code
                      style={{
                        fontSize: "12px",
                        fontFamily: "var(--font-mono)",
                        color: "var(--text-secondary)",
                        background: "var(--bg-tertiary)",
                        padding: "3px 8px",
                        borderRadius: "4px",
                      }}
                    >
                      {agent.model}
                    </code>
                  </td>
                  <td
                    style={{
                      padding: "14px 18px",
                      fontSize: "13px",
                      color: "var(--text-secondary)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    v{agent.version}
                  </td>
                  <td style={{ padding: "14px 18px" }}>
                    <StatusBadge status={agent.status} />
                  </td>
                  <td
                    style={{
                      padding: "14px 18px",
                      fontSize: "12px",
                      color: "var(--text-tertiary)",
                    }}
                  >
                    {formatDate(agent.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {isRegisterModalOpen && (
        <RegisterAgentModal
          isOpen={isRegisterModalOpen}
          onClose={() => setIsRegisterModalOpen(false)}
          onSuccess={() => loadAgents()}
        />
      )}
    </div>
  );
}
