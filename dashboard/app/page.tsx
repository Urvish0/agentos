"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Agent, Task, DashboardStats } from "@/lib/types";
import { fetchAgents, fetchTasks } from "@/lib/api";

/**
 * Dashboard Home Page — Summary cards with quick stats.
 */
export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats>({
    totalAgents: 0,
    activeAgents: 0,
    inactiveAgents: 0,
    archivedAgents: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskCount, setTaskCount] = useState({ total: 0, running: 0 });

  useEffect(() => {
    Promise.all([fetchAgents(), fetchTasks()])
      .then(([agents, tasks]: [Agent[], Task[]]) => {
        setStats({
          totalAgents: agents.length,
          activeAgents: agents.filter((a) => a.status === "active").length,
          inactiveAgents: agents.filter((a) => a.status === "inactive").length,
          archivedAgents: agents.filter((a) => a.status === "archived").length,
        });
        setTaskCount({
          total: tasks.length,
          running: tasks.filter((t) => t.status === "running").length,
        });
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const statCards = [
    {
      label: "Total Agents",
      value: stats.totalAgents,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="8" r="4" />
          <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
        </svg>
      ),
      color: "var(--accent-cyan)",
      href: "/agents",
    },
    {
      label: "Active",
      value: stats.activeAgents,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--status-active)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
      ),
      color: "var(--status-active)",
      href: "/agents",
    },
    {
      label: "Inactive",
      value: stats.inactiveAgents,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--status-inactive)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
        </svg>
      ),
      color: "var(--status-inactive)",
      href: "/agents",
    },
    {
      label: "Archived",
      value: stats.archivedAgents,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--status-archived)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="21 8 21 21 3 21 3 8" />
          <rect x="1" y="3" width="22" height="5" />
          <line x1="10" y1="12" x2="14" y2="12" />
        </svg>
      ),
      color: "var(--status-archived)",
      href: "/agents",
    },
    {
      label: "Total Tasks",
      value: taskCount.total,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="hsl(210, 90%, 65%)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 11l3 3L22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
      ),
      color: "hsl(210, 90%, 65%)",
      href: "/tasks",
    },
    {
      label: "Running",
      value: taskCount.running,
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="hsl(270, 50%, 65%)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
      ),
      color: "hsl(270, 50%, 65%)",
      href: "/tasks",
    },
  ];

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <h1
          style={{
            fontSize: "26px",
            fontWeight: 700,
            color: "var(--text-primary)",
            letterSpacing: "-0.02em",
            margin: 0,
          }}
        >
          Dashboard
        </h1>
        <p
          style={{
            fontSize: "14px",
            color: "var(--text-secondary)",
            marginTop: "6px",
          }}
        >
          Welcome to AgentOS — your infrastructure platform for AI agents.
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div
          style={{
            padding: "14px 18px",
            background: "hsl(0, 70%, 55% / 0.1)",
            border: "1px solid hsl(0, 70%, 55% / 0.25)",
            borderRadius: "var(--radius-md)",
            color: "var(--accent-red)",
            fontSize: "13px",
            marginBottom: "24px",
          }}
        >
          <strong>Connection Error:</strong> Could not reach the backend API.
          Make sure the AgentOS server is running on{" "}
          <code style={{ fontFamily: "var(--font-mono)" }}>
            localhost:8000
          </code>
          .
        </div>
      )}

      {/* Stats Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "16px",
          marginBottom: "40px",
        }}
      >
        {statCards.map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="card"
            style={{
              padding: "22px 20px",
              textDecoration: "none",
              cursor: "pointer",
              display: "block",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "14px",
              }}
            >
              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "var(--text-secondary)",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                }}
              >
                {card.label}
              </span>
              {card.icon}
            </div>
            <div
              style={{
                fontSize: loading ? "14px" : "32px",
                fontWeight: 700,
                color: loading ? "var(--text-tertiary)" : "var(--text-primary)",
                letterSpacing: "-0.02em",
              }}
            >
              {loading ? (
                <div className="skeleton" style={{ width: 50, height: 36 }} />
              ) : (
                card.value
              )}
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Links */}
      <div style={{ marginBottom: "24px" }}>
        <h2
          style={{
            fontSize: "16px",
            fontWeight: 600,
            color: "var(--text-primary)",
            marginBottom: "14px",
          }}
        >
          Quick Actions
        </h2>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <Link
            href="/agents"
            style={{
              padding: "10px 20px",
              background: "var(--bg-tertiary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-primary)",
              fontSize: "13px",
              fontWeight: 500,
              textDecoration: "none",
              transition: "all var(--transition-fast)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--accent-cyan)";
              e.currentTarget.style.background = "var(--accent-cyan-glow)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border-primary)";
              e.currentTarget.style.background = "var(--bg-tertiary)";
            }}
          >
            View All Agents →
          </Link>
          <Link
            href="/tasks"
            style={{
              padding: "10px 20px",
              background: "var(--bg-tertiary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-primary)",
              fontSize: "13px",
              fontWeight: 500,
              textDecoration: "none",
              transition: "all var(--transition-fast)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "var(--accent-cyan)";
              e.currentTarget.style.background = "var(--accent-cyan-glow)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border-primary)";
              e.currentTarget.style.background = "var(--bg-tertiary)";
            }}
          >
            View All Tasks →
          </Link>
        </div>
      </div>
    </div>
  );
}
