"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Task, TaskStats } from "@/lib/types";
import { fetchTasks } from "@/lib/api";
import TaskStatusBadge from "@/components/TaskStatusBadge";

const STATUS_FILTERS = [
  { label: "All", value: "" },
  { label: "Running", value: "running" },
  { label: "Queued", value: "queued" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
  { label: "Cancelled", value: "cancelled" },
];

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const loadTasks = () => {
    setLoading(true);
    fetchTasks(statusFilter ? { status: statusFilter } : undefined)
      .then(setTasks)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTasks();
    // Auto-refresh every 5 seconds for real-time monitoring
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const stats: TaskStats = {
    total: tasks.length,
    running: tasks.filter((t) => t.status === "running").length,
    completed: tasks.filter((t) => t.status === "completed").length,
    failed: tasks.filter((t) => t.status === "failed").length,
    queued: tasks.filter((t) => t.status === "queued").length,
    cancelled: tasks.filter((t) => t.status === "cancelled").length,
  };

  const filteredTasks = tasks.filter(
    (task) =>
      task.input.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.agent_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (iso: string) => {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  const formatDuration = (ms: number) => {
    if (ms === 0) return "—";
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const miniStatCards = [
    { label: "Running", value: stats.running, color: "hsl(210, 90%, 65%)" },
    { label: "Queued", value: stats.queued, color: "hsl(270, 50%, 65%)" },
    { label: "Completed", value: stats.completed, color: "hsl(160, 70%, 55%)" },
    { label: "Failed", value: stats.failed, color: "hsl(0, 70%, 60%)" },
  ];

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "24px",
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
            Tasks
          </h1>
          <p
            style={{
              fontSize: "14px",
              color: "var(--text-secondary)",
              marginTop: "6px",
            }}
          >
            {loading
              ? "Loading tasks..."
              : `${stats.total} task${stats.total !== 1 ? "s" : ""} • Auto-refreshing every 5s`}
          </p>
        </div>
      </div>

      {/* Mini Stats Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
          gap: "10px",
          marginBottom: "20px",
        }}
      >
        {miniStatCards.map((card) => (
          <div
            key={card.label}
            className="card"
            style={{ padding: "14px 16px" }}
          >
            <div
              style={{
                fontSize: "11px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                color: "var(--text-tertiary)",
                marginBottom: "6px",
              }}
            >
              {card.label}
            </div>
            <div
              style={{
                fontSize: "24px",
                fontWeight: 700,
                color: loading ? "var(--text-tertiary)" : card.color,
                letterSpacing: "-0.02em",
              }}
            >
              {loading ? (
                <div className="skeleton" style={{ width: 36, height: 28 }} />
              ) : (
                card.value
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Filters + Search Row */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          marginBottom: "20px",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        {/* Status filter pills */}
        <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
          {STATUS_FILTERS.map((filter) => (
            <button
              key={filter.value}
              onClick={() => setStatusFilter(filter.value)}
              style={{
                padding: "6px 14px",
                borderRadius: "var(--radius-sm)",
                fontSize: "12px",
                fontWeight: 500,
                border: "1px solid",
                borderColor:
                  statusFilter === filter.value
                    ? "var(--accent-cyan)"
                    : "var(--border-primary)",
                background:
                  statusFilter === filter.value
                    ? "var(--accent-cyan-glow)"
                    : "var(--bg-secondary)",
                color:
                  statusFilter === filter.value
                    ? "var(--text-accent)"
                    : "var(--text-secondary)",
                cursor: "pointer",
                transition: "all var(--transition-fast)",
                fontFamily: "inherit",
              }}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div style={{ position: "relative", flex: "1", minWidth: "200px", maxWidth: "340px" }}>
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--text-tertiary)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              position: "absolute",
              left: "12px",
              top: "50%",
              transform: "translateY(-50%)",
            }}
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search by input, ID, or agent..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "8px 12px 8px 36px",
              background: "var(--bg-secondary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-sm)",
              color: "var(--text-primary)",
              fontSize: "12.5px",
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
          className="card"
          style={{ padding: "40px", textAlign: "center" }}
        >
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--accent-red)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 12 }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 6px" }}>
            Cannot reach backend
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
            Make sure the AgentOS server is running on{" "}
            <code style={{ fontFamily: "var(--font-mono)", background: "var(--bg-tertiary)", padding: "2px 6px", borderRadius: "4px" }}>localhost:8000</code>
          </p>
        </div>
      )}

      {/* Loading State */}
      {loading && !error && (
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="skeleton"
              style={{ height: "58px", borderRadius: "var(--radius-md)" }}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && tasks.length === 0 && (
        <div className="card" style={{ padding: "60px 40px", textAlign: "center" }}>
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 14, opacity: 0.6 }}>
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
          <h3 style={{ fontSize: "17px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 8px" }}>
            No tasks yet
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: "0 0 20px", maxWidth: "380px", marginInline: "auto" }}>
            Create your first task using the CLI or API:
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
            agentos tasks create --agent &lt;ID&gt; --input &quot;Your task&quot;
          </code>
        </div>
      )}

      {/* No Search Results */}
      {!loading && !error && tasks.length > 0 && filteredTasks.length === 0 && (
        <div className="card" style={{ padding: "40px", textAlign: "center" }}>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            No tasks match &ldquo;<strong>{searchQuery}</strong>&rdquo;
          </p>
        </div>
      )}

      {/* Task Table */}
      {!loading && !error && filteredTasks.length > 0 && (
        <div className="card" style={{ overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-primary)" }}>
                {["Input", "Status", "Agent", "Model", "Tokens", "Duration", "Created"].map(
                  (header) => (
                    <th
                      key={header}
                      style={{
                        padding: "11px 16px",
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
              {filteredTasks.map((task) => (
                <tr
                  key={task.id}
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
                  <td style={{ padding: "12px 16px", maxWidth: "280px" }}>
                    <Link
                      href={`/tasks/${task.id}`}
                      style={{ textDecoration: "none", display: "block" }}
                    >
                      <div
                        style={{
                          fontSize: "13px",
                          fontWeight: 500,
                          color: "var(--text-primary)",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {task.input}
                      </div>
                      <div
                        style={{
                          fontSize: "11px",
                          color: "var(--text-tertiary)",
                          fontFamily: "var(--font-mono)",
                          marginTop: "2px",
                        }}
                      >
                        {task.id.slice(0, 8)}…
                      </div>
                    </Link>
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <TaskStatusBadge status={task.status} />
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      fontSize: "11.5px",
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {task.agent_id.slice(0, 8)}…
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    {task.model ? (
                      <code
                        style={{
                          fontSize: "11.5px",
                          fontFamily: "var(--font-mono)",
                          color: "var(--text-secondary)",
                          background: "var(--bg-tertiary)",
                          padding: "2px 7px",
                          borderRadius: "4px",
                        }}
                      >
                        {task.model}
                      </code>
                    ) : (
                      <span style={{ color: "var(--text-tertiary)", fontSize: "12px" }}>—</span>
                    )}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {task.total_tokens > 0 ? task.total_tokens.toLocaleString() : "—"}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {formatDuration(task.execution_time_ms)}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      fontSize: "12px",
                      color: "var(--text-tertiary)",
                    }}
                  >
                    {formatDate(task.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
