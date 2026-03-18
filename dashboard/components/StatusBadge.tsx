/**
 * StatusBadge — Displays an agent's status with color-coding.
 */

interface StatusBadgeProps {
  status: "active" | "inactive" | "archived" | string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase();

  let className = "badge ";
  let dotClass = "pulse-dot ";

  switch (normalized) {
    case "active":
      className += "badge-active";
      dotClass += "pulse-dot-active";
      break;
    case "inactive":
      className += "badge-inactive";
      dotClass += "pulse-dot-inactive";
      break;
    case "archived":
      className += "badge-archived";
      dotClass += "pulse-dot-archived";
      break;
    default:
      className += "badge-archived";
      dotClass += "pulse-dot-archived";
  }

  return (
    <span className={className}>
      <span className={dotClass} />
      {normalized}
    </span>
  );
}
