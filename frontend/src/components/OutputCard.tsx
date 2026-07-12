import { useState } from "react";

interface Props { title: string; content: string; }

export default function OutputCard({ title, content }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      border: "1px solid #1a2a3a",
      borderRadius: 4,
      background: "#0d1520",
      marginBottom: "1rem",
      overflow: "hidden",
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "8px 12px",
        borderBottom: "1px solid #0d1a24",
        background: "#0a1520",
      }}>
        <span style={{ fontSize: 10, color: "#00ff9d", letterSpacing: 2, fontWeight: 700 }}>
          {title.toUpperCase()}
        </span>
        <button
          onClick={handleCopy}
          style={{
            fontSize: 10,
            padding: "3px 10px",
            borderRadius: 2,
            border: `1px solid ${copied ? "#00ff9d" : "#1a2a3a"}`,
            background: copied ? "#00ff9d15" : "transparent",
            cursor: "pointer",
            color: copied ? "#00ff9d" : "#2d5a44",
            fontFamily: "inherit",
            letterSpacing: 1,
          }}
        >
          {copied ? "✓ COPIED" : "[ COPY ]"}
        </button>
      </div>
      <pre style={{
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        fontSize: 12,
        color: "#8fcca8",
        margin: 0,
        fontFamily: "inherit",
        lineHeight: 1.7,
        padding: "1rem",
      }}>
        {content}
      </pre>
    </div>
  );
}
