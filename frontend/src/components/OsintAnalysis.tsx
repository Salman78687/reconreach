import { useState } from "react";

type SourceEntry = { status: string; data: unknown; note?: string };
interface Props { rawAnalysis: Record<string, SourceEntry>; }

const STATUS_STYLE: Record<string, { color: string; bg: string; label: string }> = {
  success: { color: "#00ff9d", bg: "#00ff9d15", label: "SUCCESS" },
  empty:   { color: "#ffaa00", bg: "#ffaa0015", label: "EMPTY"   },
  error:   { color: "#ff4040", bg: "#ff404015", label: "ERROR"   },
  skipped: { color: "#2d5a44", bg: "transparent", label: "SKIP"  },
  invalid: { color: "#ff4040", bg: "#ff404015", label: "INVALID" },
};

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_STYLE[status] ?? STATUS_STYLE.skipped;
  return (
    <span style={{
      fontSize: 9,
      padding: "2px 6px",
      borderRadius: 2,
      fontWeight: 700,
      letterSpacing: 1,
      color: s.color,
      background: s.bg,
      border: `1px solid ${s.color}44`,
      fontFamily: "inherit",
      flexShrink: 0,
    }}>
      {s.label}
    </span>
  );
}

function SourceRow({ name, entry }: { name: string; entry: SourceEntry }) {
  const [open, setOpen] = useState(false);
  const hasData = entry.data !== null && entry.data !== undefined &&
    (Array.isArray(entry.data)
      ? (entry.data as unknown[]).length > 0
      : Object.keys(entry.data as object).length > 0);

  return (
    <div style={{ borderBottom: "1px solid #0d1a24" }}>
      <button
        onClick={() => setOpen(o => !o)}
        disabled={!hasData}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "8px 0",
          background: "none",
          border: "none",
          cursor: hasData ? "pointer" : "default",
          textAlign: "left",
        }}
      >
        <span style={{
          fontSize: 11,
          color: hasData ? "#5a9e7a" : "#1a3a2a",
          fontFamily: "inherit",
          fontWeight: 600,
          flex: 1,
          letterSpacing: 0.3,
        }}>
          {hasData ? "▸ " : "  "}{name}
        </span>
        {entry.note && (
          <span style={{ fontSize: 10, color: "#1a3a2a", fontStyle: "italic" }}>{entry.note}</span>
        )}
        <StatusBadge status={entry.status} />
      </button>
      {open && hasData && (
        <pre style={{
          margin: "0 0 8px",
          padding: "10px 12px",
          background: "#030608",
          border: "1px solid #0d1a24",
          borderRadius: 3,
          fontSize: 11,
          color: "#00ff9d99",
          overflowX: "auto",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          lineHeight: 1.6,
          fontFamily: "inherit",
        }}>
          {JSON.stringify(entry.data, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function OsintAnalysis({ rawAnalysis }: Props) {
  const entries = Object.entries(rawAnalysis);
  if (entries.length === 0) return null;
  const successCount = entries.filter(([, e]) => e.status === "success").length;

  return (
    <div style={{
      border: "1px solid #1a2a3a",
      borderRadius: 4,
      padding: "1rem",
      background: "#0d1520",
      marginBottom: "1rem",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ fontSize: 10, color: "#00ff9d", letterSpacing: 2, fontWeight: 700 }}>
          OSINT ANALYSIS
        </span>
        <span style={{ fontSize: 10, color: "#2d5a44", letterSpacing: 0.5 }}>
          {successCount}/{entries.length} sources hit
        </span>
      </div>
      {entries.map(([name, entry]) => (
        <SourceRow key={name} name={name} entry={entry} />
      ))}
    </div>
  );
}
