import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { enrichmentApi, leadsApi, type Lead } from "../api/client";
import EnrichmentStatusBadge from "../components/EnrichmentStatus";
import LeadUploader from "../components/LeadUploader";

const G = "#00ff9d";
const C2 = "#00c4f0";

const C = {
  bg:         "#060b14",
  card:       "#0d1520",
  elevated:   "#111d2e",
  border:     "#1a2a3a",
  text:       "#c8fce0",
  textSub:    "#5a9e7a",
  textMuted:  "#2d5a44",
  accent:     G,
  accent2:    C2,
  error:      "#ff4040",
  warning:    "#ffaa00",
};

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [singleValue, setSingleValue] = useState("");
  const [singleLoading, setSingleLoading] = useState(false);
  const [singleError, setSingleError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const fetchLeads = async () => {
    try {
      const data = await leadsApi.list();
      setLeads(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleUploaded = (newLeads: Lead[]) => {
    setLeads((prev) => [...newLeads, ...prev]);
  };

  const handleAddSingle = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = singleValue.trim();
    if (!value) return;
    setSingleLoading(true);
    setSingleError(null);
    try {
      const lead = await leadsApi.addSingle(value);
      setLeads((prev) => [lead, ...prev]);
      setSingleValue("");
      inputRef.current?.focus();
      await enrichmentApi.enrich(lead.id);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      setSingleError(detail ?? "Failed to add lead.");
    } finally {
      setSingleLoading(false);
    }
  };

  const handleEnrichAll = async () => {
    await enrichmentApi.enrichAll();
    fetchLeads();
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    await leadsApi.delete(id);
    setLeads((prev) => prev.filter((l) => l.id !== id));
  };

  const doneCount = leads.filter(l => l.enrichment_status === "done").length;
  const inProgressCount = leads.filter(l => l.enrichment_status === "in_progress").length;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── Top nav bar ─────────────────────────────────────────────── */}
      <div
        className="scanline-container"
        style={{
          borderBottom: `1px solid ${C.border}`,
          background: "linear-gradient(180deg, #0a1520 0%, #060b14 100%)",
          padding: "0 2rem",
        }}
      >
        <div style={{ maxWidth: 1600, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", height: 60 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ color: G, fontSize: 18, fontWeight: 700, letterSpacing: 2 }} className="anim-flicker">
                ▣
              </span>
              <span style={{ color: C.text, fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>
                OSINT_COLDCALL
              </span>
              <span style={{ color: C.textMuted, fontSize: 11 }}>.exe</span>
            </div>
            <span style={{ color: C.border, fontSize: 12 }}>|</span>
            <span style={{ color: C.textSub, fontSize: 11, letterSpacing: 0.5 }}>
              ENRICHMENT PIPELINE v2.0
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            {leads.length > 0 && (
              <div style={{ display: "flex", gap: 12, fontSize: 11, color: C.textSub }}>
                <span>
                  <span style={{ color: G }}>{doneCount}</span> DONE
                </span>
                {inProgressCount > 0 && (
                  <span>
                    <span style={{ color: C2, animation: "blink 1s step-end infinite" }}>{inProgressCount}</span> SCANNING
                  </span>
                )}
                <span>
                  <span style={{ color: C.textSub }}>{leads.length}</span> TOTAL
                </span>
              </div>
            )}
            <button
              onClick={() => navigate("/settings")}
              style={{
                padding: "5px 14px",
                border: `1px solid ${C.border}`,
                borderRadius: 3,
                background: "transparent",
                cursor: "pointer",
                fontSize: 11,
                color: C.textSub,
                fontFamily: "inherit",
                letterSpacing: 1,
              }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = G; (e.currentTarget as HTMLElement).style.color = G; }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = C.border; (e.currentTarget as HTMLElement).style.color = C.textSub; }}
            >
              [SETTINGS]
            </button>
          </div>
        </div>
      </div>

      {/* ── Hero heading ─────────────────────────────────────────────── */}
      <div
        style={{
          borderBottom: `1px solid ${C.border}`,
          padding: "2.5rem 2rem",
          background: "linear-gradient(180deg, #0a1520 0%, transparent 100%)",
        }}
      >
        <div style={{ maxWidth: 1600, margin: "0 auto" }}>
          <div style={{ marginBottom: 6 }}>
            <span style={{ color: C.textMuted, fontSize: 12, letterSpacing: 1 }}>
              &gt; initializing target enrichment pipeline...
            </span>
          </div>
          <h1
            className="cursor-blink"
            style={{
              margin: 0,
              fontSize: 32,
              fontWeight: 700,
              color: G,
              letterSpacing: 2,
              textShadow: `0 0 20px ${G}66, 0 0 40px ${G}33`,
              fontFamily: "inherit",
            }}
          >
            OSINT COLD OUTREACH
          </h1>
          <p style={{ margin: "8px 0 0", color: C.textSub, fontSize: 13, letterSpacing: 0.5 }}>
            Passive intelligence gathering → personalized outreach generation
          </p>
        </div>
      </div>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <div style={{ flex: 1, padding: "2rem", maxWidth: 1600, margin: "0 auto", width: "100%" }}>

        {/* Input row */}
        <form onSubmit={handleAddSingle} style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", gap: 0 }}>
            <div style={{ display: "flex", alignItems: "center", background: C.card, border: `1px solid ${C.border}`, borderRight: "none", borderRadius: "3px 0 0 3px", padding: "0 12px" }}>
              <span style={{ color: G, fontSize: 13, userSelect: "none" }}>&gt;_</span>
            </div>
            <input
              ref={inputRef}
              type="text"
              value={singleValue}
              onChange={(e) => { setSingleValue(e.target.value); setSingleError(null); }}
              placeholder="target@domain.com or +1234567890"
              disabled={singleLoading}
              style={{
                flex: 1,
                padding: "12px 16px",
                background: C.card,
                border: `1px solid ${C.border}`,
                borderRight: "none",
                color: C.text,
                fontSize: 14,
                fontFamily: "inherit",
                letterSpacing: 0.3,
              }}
            />
            <button
              type="submit"
              disabled={singleLoading || !singleValue.trim()}
              style={{
                padding: "12px 24px",
                background: singleLoading || !singleValue.trim() ? C.card : G,
                color: singleLoading || !singleValue.trim() ? C.textMuted : "#060b14",
                border: `1px solid ${singleLoading || !singleValue.trim() ? C.border : G}`,
                borderRadius: "0 3px 3px 0",
                fontSize: 12,
                fontWeight: 700,
                fontFamily: "inherit",
                letterSpacing: 1,
                cursor: singleLoading || !singleValue.trim() ? "not-allowed" : "pointer",
                whiteSpace: "nowrap",
              }}
            >
              {singleLoading ? "SCANNING…" : "[ SCAN TARGET ]"}
            </button>
          </div>
          {singleError && (
            <p style={{ margin: "6px 0 0", fontSize: 12, color: C.error, letterSpacing: 0.3 }}>
              ✗ {singleError}
            </p>
          )}
        </form>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "1.5rem" }}>
          <div style={{ flex: 1, height: 1, background: `linear-gradient(to right, transparent, ${C.border})` }} />
          <span style={{ fontSize: 11, color: C.textMuted, letterSpacing: 1 }}>OR UPLOAD CSV</span>
          <div style={{ flex: 1, height: 1, background: `linear-gradient(to left, transparent, ${C.border})` }} />
        </div>

        <LeadUploader onUploaded={handleUploaded} />

        {/* Leads table section */}
        <div style={{ marginTop: "2.5rem" }}>
          {leads.length > 0 && (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ color: G, fontSize: 11, letterSpacing: 2, fontWeight: 700 }}>TARGETS</span>
                <span
                  style={{
                    background: "#00ff9d15",
                    border: `1px solid ${G}44`,
                    color: G,
                    fontSize: 11,
                    padding: "1px 8px",
                    borderRadius: 2,
                    letterSpacing: 1,
                  }}
                >
                  {leads.length}
                </span>
              </div>
              <button
                onClick={handleEnrichAll}
                style={{
                  padding: "7px 20px",
                  background: "transparent",
                  color: C2,
                  border: `1px solid ${C2}`,
                  borderRadius: 3,
                  cursor: "pointer",
                  fontSize: 11,
                  fontWeight: 700,
                  fontFamily: "inherit",
                  letterSpacing: 1,
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = `${C2}15`; }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}
              >
                [ ENRICH ALL ]
              </button>
            </div>
          )}

          {loading ? (
            <div style={{ color: C.textSub, textAlign: "center", padding: "3rem", fontSize: 13, letterSpacing: 1 }}>
              &gt; loading targets<span className="cursor-blink" />
            </div>
          ) : leads.length === 0 ? (
            <div
              style={{
                textAlign: "center",
                padding: "4rem 2rem",
                border: `1px dashed ${C.border}`,
                borderRadius: 4,
                color: C.textMuted,
              }}
              className="anim-fade-in"
            >
              <div style={{ fontSize: 28, marginBottom: 12, color: C.border }}>◈</div>
              <p style={{ fontSize: 13, color: C.textSub, letterSpacing: 0.5 }}>No targets loaded</p>
              <p style={{ fontSize: 11, color: C.textMuted, marginTop: 6 }}>Add an email, phone number, or upload a CSV to begin</p>
            </div>
          ) : (
            <div
              style={{
                border: `1px solid ${C.border}`,
                borderRadius: 4,
                overflow: "hidden",
              }}
              className="anim-fade-in"
            >
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#0a1520", borderBottom: `1px solid ${C.border}` }}>
                    {[
                      { label: "TARGET", w: "30%" },
                      { label: "TYPE", w: "8%" },
                      { label: "NAME", w: "16%" },
                      { label: "COMPANY", w: "18%" },
                      { label: "SCORE", w: "8%" },
                      { label: "STATUS", w: "12%" },
                      { label: "", w: "4%" },
                    ].map((h) => (
                      <th
                        key={h.label}
                        style={{
                          textAlign: "left",
                          padding: "10px 16px",
                          fontSize: 10,
                          color: C.textMuted,
                          fontWeight: 700,
                          letterSpacing: 1.5,
                          width: h.w,
                          fontFamily: "inherit",
                        }}
                      >
                        {h.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead) => (
                    <tr
                      key={lead.id}
                      className="lead-row"
                      onClick={() => navigate(`/leads/${lead.id}`)}
                      style={{
                        borderBottom: `1px solid ${C.border}`,
                        cursor: "pointer",
                        background: C.card,
                      }}
                      onMouseEnter={(e) => {
                        const el = e.currentTarget as HTMLElement;
                        el.style.background = C.elevated;
                        el.style.boxShadow = `inset 3px 0 0 ${G}`;
                      }}
                      onMouseLeave={(e) => {
                        const el = e.currentTarget as HTMLElement;
                        el.style.background = C.card;
                        el.style.boxShadow = "none";
                      }}
                    >
                      <td style={{ padding: "12px 16px", fontSize: 13, color: C.text, fontFamily: "inherit" }}>
                        {lead.input_value}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <span
                          style={{
                            fontSize: 10,
                            padding: "2px 7px",
                            borderRadius: 2,
                            background: lead.input_type === "email" ? "#001a2e" : "#1a001a",
                            color: lead.input_type === "email" ? C2 : "#cc88ff",
                            fontWeight: 700,
                            border: `1px solid ${lead.input_type === "email" ? C2 + "44" : "#cc88ff44"}`,
                            letterSpacing: 0.5,
                            fontFamily: "inherit",
                          }}
                        >
                          {lead.input_type}
                        </span>
                      </td>
                      <td style={{ padding: "12px 16px", fontSize: 12, color: C.textSub, fontFamily: "inherit" }}>
                        {lead.name ?? <span style={{ color: C.textMuted }}>—</span>}
                      </td>
                      <td style={{ padding: "12px 16px", fontSize: 12, color: C.textSub, fontFamily: "inherit" }}>
                        {lead.company_name ?? <span style={{ color: C.textMuted }}>—</span>}
                      </td>
                      <td style={{ padding: "12px 16px", fontSize: 12, fontFamily: "inherit" }}>
                        {lead.enrichment_score > 0 ? (
                          <span style={{ color: G }}>{lead.enrichment_score}%</span>
                        ) : (
                          <span style={{ color: C.textMuted }}>—</span>
                        )}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <EnrichmentStatusBadge status={lead.enrichment_status} />
                      </td>
                      <td style={{ padding: "12px 16px", textAlign: "center" }}>
                        <button
                          onClick={(e) => handleDelete(lead.id, e)}
                          style={{
                            background: "none",
                            border: "none",
                            color: C.textMuted,
                            cursor: "pointer",
                            fontSize: 16,
                            lineHeight: 1,
                            padding: "2px 4px",
                            fontFamily: "inherit",
                          }}
                          onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.color = C.error)}
                          onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.color = C.textMuted)}
                          title="Delete target"
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <div
        style={{
          borderTop: `1px solid ${C.border}`,
          padding: "0.75rem 2rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1 }}>
          FREE TIER — GitHub · Gravatar · WHOIS · EmailRep · LinkedIn
        </span>
        <span style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1 }}>
          SYSTEM ONLINE <span style={{ color: G }}>●</span>
        </span>
      </div>
    </div>
  );
}
