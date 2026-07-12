import { useState } from "react";
import type { GenerationRequest } from "../api/client";

interface Props {
  onGenerate: (req: Omit<GenerationRequest, "output_types">) => void;
  loading: boolean;
}

export default function ProductForm({ onGenerate, loading }: Props) {
  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [keyValueProps, setKeyValueProps] = useState("");
  const [targetPainPoint, setTargetPainPoint] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      product_name: productName,
      product_description: productDescription,
      key_value_props: keyValueProps.split("\n").map(s => s.trim()).filter(Boolean),
      target_pain_point: targetPainPoint,
    });
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "8px 10px",
    borderRadius: 3,
    border: "1px solid #1a2a3a",
    background: "#060b14",
    color: "#c8fce0",
    fontSize: 12,
    fontFamily: "inherit",
    letterSpacing: 0.3,
    boxSizing: "border-box",
  };

  const labelStyle: React.CSSProperties = {
    fontSize: 10,
    fontWeight: 700,
    color: "#2d5a44",
    display: "block",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 1.5,
    fontFamily: "inherit",
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div>
        <label style={labelStyle}>Product / Service</label>
        <input style={inputStyle} value={productName} onChange={e => setProductName(e.target.value)}
          placeholder="e.g. Acme Analytics" required />
      </div>
      <div>
        <label style={labelStyle}>Description</label>
        <textarea style={{ ...inputStyle, height: 64, resize: "vertical" }}
          value={productDescription} onChange={e => setProductDescription(e.target.value)}
          placeholder="What does your product do?" required />
      </div>
      <div>
        <label style={labelStyle}>
          Value Props <span style={{ fontWeight: 400, textTransform: "none", letterSpacing: 0 }}>(one per line)</span>
        </label>
        <textarea style={{ ...inputStyle, height: 60, resize: "vertical" }}
          value={keyValueProps} onChange={e => setKeyValueProps(e.target.value)}
          placeholder={"Saves 10 hours/week\nReduces errors by 80%"} />
      </div>
      <div>
        <label style={labelStyle}>Pain Point</label>
        <input style={inputStyle} value={targetPainPoint} onChange={e => setTargetPainPoint(e.target.value)}
          placeholder="e.g. Manual reporting is slow" required />
      </div>
      <button
        type="submit"
        disabled={loading}
        style={{
          padding: "10px",
          background: loading ? "transparent" : "#00ff9d",
          color: loading ? "#2d5a44" : "#060b14",
          border: `1px solid ${loading ? "#1a2a3a" : "#00ff9d"}`,
          borderRadius: 3,
          fontSize: 11,
          fontWeight: 700,
          fontFamily: "inherit",
          letterSpacing: 1.5,
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "> GENERATING…" : "[ GENERATE OUTREACH ]"}
      </button>
    </form>
  );
}
