"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Task } from "@/lib/types";
import { fetchTask, cancelTask } from "@/lib/api";
import TaskStatusBadge from "@/components/TaskStatusBadge";

export default function TaskDetailPage() {
  const params = useParams();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  const loadTask = () => {
    if (!taskId) return;
    fetchTask(taskId)
      .then(setTask)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTask();
    // Auto-refresh while task is not in a terminal state
    const interval = setInterval(loadTask, 3000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const handleCancel = async () => {
    if (!task) return;
    setCancelling(true);
    try {
      const updated = await cancelTask(task.id);
      setTask(updated);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      alert(`Failed to cancel: ${message}`);
    } finally {
      setCancelling(false);
    }
  };

  const formatDate = (iso: string) => {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  const formatDuration = (ms: number) => {
    if (ms === 0) return "—";
    if (ms < 1000) return `${Math.round(ms)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${(ms / 60000).toFixed(1)}min`;
  };

  const isTerminal = task
    ? ["completed", "failed", "cancelled"].includes(task.status)
    : false;
  const isCancellable = task
    ? ["running", "queued", "paused"].includes(task.status)
    : false;

  // Loading
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

  // Error
  if (error || !task) {
    return (
      <div className="animate-fade-in">
        <Link href="/tasks" style={{ fontSize: "13px", color: "var(--text-secondary)", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "6px", marginBottom: "24px" }}>
          ← Back to Tasks
        </Link>
        <div className="card" style={{ padding: "60px 40px", textAlign: "center" }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--accent-red)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 14 }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 6px" }}>
            Task not found
          </h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
            {error || `No task found with ID: ${taskId}`}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Breadcrumb */}
      <Link
        href="/tasks"
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
        ← Back to Tasks
      </Link>

      {/* Task Header */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "16px",
          marginBottom: "28px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "6px" }}>
            <h1
              style={{
                fontSize: "22px",
                fontWeight: 700,
                color: "var(--text-primary)",
                letterSpacing: "-0.02em",
                margin: 0,
              }}
            >
              Task Detail
            </h1>
            <TaskStatusBadge status={task.status} />
            {!isTerminal && (
              <span
                style={{
                  fontSize: "11px",
                  color: "var(--text-tertiary)",
                  fontStyle: "italic",
                }}
              >
                Auto-refreshing…
              </span>
            )}
          </div>
          <p
            style={{
              fontSize: "12px",
              fontFamily: "var(--font-mono)",
              color: "var(--text-tertiary)",
              margin: 0,
            }}
          >
            {task.id}
          </p>
        </div>

        {/* Cancel button */}
        {isCancellable && (
          <button
            onClick={handleCancel}
            disabled={cancelling}
            style={{
              padding: "8px 18px",
              borderRadius: "var(--radius-sm)",
              fontSize: "12.5px",
              fontWeight: 600,
              border: "1px solid hsl(0, 70%, 55% / 0.4)",
              background: "hsl(0, 70%, 55% / 0.1)",
              color: "var(--accent-red)",
              cursor: cancelling ? "wait" : "pointer",
              opacity: cancelling ? 0.6 : 1,
              transition: "all var(--transition-fast)",
              fontFamily: "inherit",
            }}
          >
            {cancelling ? "Cancelling…" : "Cancel Task"}
          </button>
        )}
      </div>

      {/* Input Card */}
      <div className="card" style={{ padding: "20px 22px", marginBottom: "16px" }}>
        <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)", margin: "0 0 10px" }}>
          Input
        </h3>
        <p style={{ fontSize: "14px", color: "var(--text-primary)", lineHeight: 1.6, margin: 0 }}>
          {task.input}
        </p>
      </div>

      {/* Metadata Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "16px",
          marginBottom: "16px",
        }}
      >
        {/* Execution Card */}
        <div className="card" style={{ padding: "20px 22px" }}>
          <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)", margin: "0 0 14px" }}>
            Execution
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <DetailRow label="Model" value={task.model || "—"} mono />
            <DetailRow label="Duration" value={formatDuration(task.execution_time_ms)} />
            <DetailRow label="Total Tokens" value={task.total_tokens > 0 ? task.total_tokens.toLocaleString() : "—"} />
          </div>
        </div>

        {/* Lifecycle Card */}
        <div className="card" style={{ padding: "20px 22px" }}>
          <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)", margin: "0 0 14px" }}>
            Lifecycle
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <DetailRow label="Retries" value={`${task.retry_count} / ${task.max_retries}`} />
            <DetailRow label="Agent ID" value={task.agent_id} mono small />
            {task.parent_task_id && (
              <DetailRow label="Parent Task" value={task.parent_task_id} mono small />
            )}
            {task.trace_id && (
              <DetailRow label="Trace ID" value={task.trace_id} mono small />
            )}
          </div>
        </div>

        {/* Timestamps Card */}
        <div className="card" style={{ padding: "20px 22px" }}>
          <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)", margin: "0 0 14px" }}>
            Timestamps
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <DetailRow label="Created" value={formatDate(task.created_at)} />
            <DetailRow label="Updated" value={formatDate(task.updated_at)} />
            <DetailRow label="Completed" value={formatDate(task.completed_at)} />
          </div>
        </div>
      </div>

      {/* Output Card */}
      {task.output && (
        <div className="card" style={{ padding: "20px 22px", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)", margin: "0 0 10px" }}>
            Output
          </h3>
          <pre
            style={{
              background: "var(--bg-primary)",
              border: "1px solid var(--border-primary)",
              borderRadius: "var(--radius-sm)",
              padding: "14px 16px",
              fontFamily: "var(--font-mono)",
              fontSize: "13px",
              color: "var(--text-secondary)",
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              margin: 0,
              overflow: "auto",
              maxHeight: "400px",
            }}
          >
            {task.output}
          </pre>
        </div>
      )}

      {/* Error Card */}
      {task.error && (
        <div
          style={{
            padding: "20px 22px",
            background: "hsl(0, 70%, 55% / 0.06)",
            border: "1px solid hsl(0, 70%, 55% / 0.2)",
            borderRadius: "var(--radius-lg)",
          }}
        >
          <h3 style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--accent-red)", margin: "0 0 10px" }}>
            Error
          </h3>
          <pre
            style={{
              background: "hsl(0, 70%, 55% / 0.05)",
              border: "1px solid hsl(0, 70%, 55% / 0.15)",
              borderRadius: "var(--radius-sm)",
              padding: "14px 16px",
              fontFamily: "var(--font-mono)",
              fontSize: "13px",
              color: "hsl(0, 70%, 70%)",
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              margin: 0,
              overflow: "auto",
              maxHeight: "300px",
            }}
          >
            {task.error}
          </pre>
        </div>
      )}
    </div>
  );
}

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
      <div style={{ fontSize: "11px", fontWeight: 500, color: "var(--text-tertiary)", marginBottom: "2px" }}>
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
