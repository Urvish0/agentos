/**
 * TaskStatusBadge — Displays a task's status with color-coding.
 *
 * Task states: created, queued, running, paused, completed, failed, cancelled
 */

interface TaskStatusBadgeProps {
  status: string;
}

const STATUS_CONFIG: Record<string, { bg: string; color: string; border: string; dotClass: string }> = {
  created: {
    bg: "hsl(220, 50%, 55% / 0.12)",
    color: "hsl(220, 50%, 65%)",
    border: "hsl(220, 50%, 55% / 0.25)",
    dotClass: "",
  },
  queued: {
    bg: "hsl(270, 50%, 55% / 0.12)",
    color: "hsl(270, 50%, 65%)",
    border: "hsl(270, 50%, 55% / 0.25)",
    dotClass: "",
  },
  running: {
    bg: "hsl(210, 90%, 55% / 0.12)",
    color: "hsl(210, 90%, 65%)",
    border: "hsl(210, 90%, 55% / 0.25)",
    dotClass: "pulse-dot-active",
  },
  paused: {
    bg: "hsl(38, 80%, 55% / 0.12)",
    color: "hsl(38, 80%, 55%)",
    border: "hsl(38, 80%, 55% / 0.25)",
    dotClass: "",
  },
  completed: {
    bg: "hsl(160, 70%, 45% / 0.12)",
    color: "hsl(160, 70%, 55%)",
    border: "hsl(160, 70%, 45% / 0.25)",
    dotClass: "",
  },
  failed: {
    bg: "hsl(0, 70%, 55% / 0.12)",
    color: "hsl(0, 70%, 60%)",
    border: "hsl(0, 70%, 55% / 0.25)",
    dotClass: "",
  },
  cancelled: {
    bg: "hsl(220, 10%, 45% / 0.12)",
    color: "hsl(220, 10%, 55%)",
    border: "hsl(220, 10%, 45% / 0.25)",
    dotClass: "",
  },
};

export default function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  const normalized = status.toLowerCase();
  const config = STATUS_CONFIG[normalized] || STATUS_CONFIG.cancelled;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "3px 10px",
        borderRadius: "999px",
        fontSize: "0.75rem",
        fontWeight: 600,
        letterSpacing: "0.02em",
        textTransform: "capitalize",
        background: config.bg,
        color: config.color,
        border: `1px solid ${config.border}`,
      }}
    >
      {config.dotClass ? (
        <span
          className={`pulse-dot ${config.dotClass}`}
          style={{ width: 6, height: 6 }}
        />
      ) : (
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: config.color,
            opacity: 0.7,
          }}
        />
      )}
      {normalized}
    </span>
  );
}
