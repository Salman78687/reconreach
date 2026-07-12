import type { EnrichmentStatus as Status } from "../api/client";

const STATUS_CONFIG: Record<Status, { label: string; color: string; bg: string; dot: string }> = {
  pending:     { label: "PENDING",    color: "#ffaa00", bg: "#1a1000", dot: "#ffaa00" },
  in_progress: { label: "SCANNING…", color: "#00c4f0", bg: "#001a22", dot: "#00c4f0" },
  done:        { label: "DONE",       color: "#00ff9d", bg: "#001a0e", dot: "#00ff9d" },
  failed:      { label: "FAILED",     color: "#ff4040", bg: "#1a0000", dot: "#ff4040" },
};

interface Props {
  status: Status;
}

export default function EnrichmentStatusBadge({ status }: Props) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending;
  const isPinging = status === "in_progress";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        padding: "3px 10px 3px 7px",
        borderRadius: 3,
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 1,
        color: cfg.color,
        background: cfg.bg,
        border: `1px solid ${cfg.color}44`,
        fontFamily: "inherit",
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: "50%",
          background: cfg.dot,
          boxShadow: `0 0 6px ${cfg.dot}`,
          flexShrink: 0,
          animation: isPinging ? "status-ping 1s ease-in-out infinite" : undefined,
        }}
      />
      {cfg.label}
    </span>
  );
}
