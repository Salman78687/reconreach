import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { leadsApi, type Lead } from "../api/client";

interface Props {
  onUploaded: (leads: Lead[]) => void;
}

export default function LeadUploader({ onUploaded }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (files: File[]) => {
      const file = files[0];
      if (!file) return;
      setLoading(true);
      setError(null);
      try {
        const leads = await leadsApi.upload(file);
        onUploaded(leads);
      } catch (e: unknown) {
        const msg =
          (e as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail ?? "Upload failed.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [onUploaded]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
    disabled: loading,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        style={{
          border: `1px dashed ${isDragActive ? "#00ff9d" : "#1a2a3a"}`,
          borderRadius: 4,
          padding: "1.75rem",
          textAlign: "center",
          cursor: loading ? "not-allowed" : "pointer",
          background: isDragActive ? "#00ff9d08" : "#0d1520",
          color: isDragActive ? "#00ff9d" : "#2d5a44",
          transition: "all 0.2s ease",
          boxShadow: isDragActive ? "0 0 20px #00ff9d22, inset 0 0 20px #00ff9d08" : "none",
        }}
      >
        <input {...getInputProps()} />
        {loading ? (
          <p style={{ margin: 0, color: "#00c4f0", fontSize: 13, letterSpacing: 1 }}>
            &gt; uploading targets<span className="cursor-blink" />
          </p>
        ) : isDragActive ? (
          <p style={{ margin: 0, fontSize: 13, letterSpacing: 1 }}>
            &gt; drop file to load targets
          </p>
        ) : (
          <div>
            <p style={{ margin: "0 0 6px", fontSize: 13, letterSpacing: 0.5 }}>
              drag & drop a CSV file, or click to select
            </p>
            <p style={{ margin: 0, fontSize: 11, color: "#1a3a2a", letterSpacing: 0.3 }}>
              required columns:{" "}
              <code style={{ color: "#5a9e7a", background: "transparent" }}>email</code>
              {" / "}
              <code style={{ color: "#5a9e7a", background: "transparent" }}>phone</code>
              {" / "}
              <code style={{ color: "#5a9e7a", background: "transparent" }}>lead</code>
            </p>
          </div>
        )}
      </div>
      {error && (
        <p style={{ color: "#ff4040", marginTop: 6, fontSize: 12, letterSpacing: 0.3 }}>✗ {error}</p>
      )}
    </div>
  );
}
