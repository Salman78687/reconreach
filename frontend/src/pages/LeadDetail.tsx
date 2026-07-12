import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { enrichmentApi, generationApi, leadsApi, type GenerationRequest, type Lead } from "../api/client";
import EnrichmentStatusBadge from "../components/EnrichmentStatus";
import OsintAnalysis from "../components/OsintAnalysis";
import OutputCard from "../components/OutputCard";
import ProductForm from "../components/ProductForm";

const G = "#00ff9d";
const C2 = "#00c4f0";
const C = {
  bg: "#060b14", card: "#0d1520", elevated: "#111d2e", border: "#1a2a3a",
  text: "#c8fce0", textSub: "#5a9e7a", textMuted: "#2d5a44",
  accent: G, accent2: C2, error: "#ff4040", warning: "#ffaa00",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ border: `1px solid ${C.border}`, borderRadius: 4, padding: "1rem", background: C.card, marginBottom: "1rem" }} className="anim-fade-up">
      <div style={{ fontSize: 10, color: G, letterSpacing: 2, fontWeight: 700, marginBottom: 10, fontFamily: "inherit" }}>
        {title.toUpperCase()}
      </div>
      {children}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return <p style={{ fontSize: 12, color: C.textMuted, margin: 0, fontStyle: "italic", fontFamily: "inherit" }}>{message}</p>;
}

function Field({ label, value, link }: { label: string; value: string | null | undefined; link?: string | null }) {
  if (!value) return null;
  return (
    <div style={{ marginBottom: 6, display: "flex", gap: 8, alignItems: "baseline" }}>
      <span style={{ fontSize: 10, color: C.textMuted, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", flexShrink: 0, fontFamily: "inherit" }}>
        {label}
      </span>
      {link ? (
        <a href={link} target="_blank" rel="noopener noreferrer"
          style={{ fontSize: 12, color: C2, textDecoration: "none", fontFamily: "inherit" }}>
          {value}
        </a>
      ) : (
        <span style={{ fontSize: 12, color: C.textSub, fontFamily: "inherit" }}>{value}</span>
      )}
    </div>
  );
}

export default function LeadDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);
  const [outputTypes, setOutputTypes] = useState<string[]>(["email", "call_script", "linkedin_msg"]);

  const fetchLead = async () => {
    if (!id) return;
    setLead(await leadsApi.get(Number(id)));
  };

  useEffect(() => {
    fetchLead();
    const interval = setInterval(fetchLead, 3000);
    return () => clearInterval(interval);
  }, [id]);

  const handleEnrich = async () => {
    if (!id) return;
    await enrichmentApi.enrich(Number(id));
    fetchLead();
  };

  const handleGenerate = async (req: Omit<GenerationRequest, "output_types">) => {
    if (!id) return;
    setGenerating(true);
    setGenError(null);
    try {
      await generationApi.generate(Number(id), { ...req, output_types: outputTypes });
      fetchLead();
    } catch (e: unknown) {
      setGenError((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Generation failed.");
    } finally {
      setGenerating(false);
    }
  };

  if (!lead) {
    return (
      <div style={{ padding: "4rem", color: C.textMuted, textAlign: "center", fontFamily: "inherit", fontSize: 13, letterSpacing: 1 }}>
        &gt; loading target<span className="cursor-blink" />
      </div>
    );
  }

  const isDone = lead.enrichment_status === "done";
  const hasNoData = isDone && lead.enrichment_score === 0;
  const hasRawAnalysis = Object.keys(lead.raw_analysis).length > 0;
  const hasOutputs = lead.generated_email || lead.generated_call_script || lead.generated_linkedin_msg;
  const hasPersonData = lead.name || lead.job_title || lead.linkedin_url || lead.twitter_url || lead.github_url || lead.bio || lead.interests.length > 0;
  const hasCompanyData = lead.company_name || lead.company_industry || lead.company_size || lead.company_website || lead.company_description;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* Top bar */}
      <div style={{ borderBottom: `1px solid ${C.border}`, background: "#0a1520", padding: "0 2rem", display: "flex", alignItems: "center", justifyContent: "space-between", height: 52 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <button
            onClick={() => navigate("/")}
            style={{ background: "none", border: "none", color: C.textSub, cursor: "pointer", fontSize: 11, fontFamily: "inherit", letterSpacing: 1, padding: 0 }}
            onMouseEnter={e => ((e.currentTarget as HTMLElement).style.color = G)}
            onMouseLeave={e => ((e.currentTarget as HTMLElement).style.color = C.textSub)}
          >
            ← TARGETS
          </button>
          <span style={{ color: C.border }}>|</span>
          <span style={{ fontSize: 11, color: C.textMuted, letterSpacing: 0.5, maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {lead.input_value}
          </span>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <EnrichmentStatusBadge status={lead.enrichment_status} />
          {lead.enrichment_status !== "in_progress" && (
            <button
              onClick={handleEnrich}
              style={{ padding: "5px 14px", background: "transparent", color: C2, border: `1px solid ${C2}44`, borderRadius: 3, cursor: "pointer", fontSize: 10, fontWeight: 700, fontFamily: "inherit", letterSpacing: 1 }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = C2; }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = `${C2}44`; }}
            >
              {isDone ? "[ RE-ENRICH ]" : "[ ENRICH ]"}
            </button>
          )}
        </div>
      </div>

      {/* Hero for this lead */}
      <div style={{ borderBottom: `1px solid ${C.border}`, background: "linear-gradient(180deg, #0a1520 0%, transparent 100%)", padding: "1.5rem 2rem" }}>
        <h1 style={{ margin: 0, fontSize: 22, color: G, fontWeight: 700, letterSpacing: 1, textShadow: `0 0 20px ${G}44`, fontFamily: "inherit" }}>
          {lead.name ?? lead.input_value}
        </h1>
        {lead.name && <p style={{ margin: "4px 0 0", color: C.textMuted, fontSize: 12, fontFamily: "inherit" }}>{lead.input_value}</p>}
        {lead.job_title && lead.company_name && (
          <p style={{ margin: "4px 0 0", color: C.textSub, fontSize: 13, fontFamily: "inherit" }}>
            {lead.job_title} @ {lead.company_name}
          </p>
        )}
        {lead.enrichment_score > 0 && (
          <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1 }}>INTEL SCORE</span>
            <div style={{ display: "flex", gap: 2 }}>
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} style={{
                  width: 16, height: 6, borderRadius: 1,
                  background: i < Math.round(lead.enrichment_score / 10) ? G : "#1a2a3a",
                  boxShadow: i < Math.round(lead.enrichment_score / 10) ? `0 0 4px ${G}88` : "none",
                }} />
              ))}
            </div>
            <span style={{ fontSize: 11, color: G }}>{lead.enrichment_score}%</span>
          </div>
        )}
      </div>

      {/* Banners */}
      <div style={{ padding: "0 2rem" }}>
        {hasNoData && (
          <div style={{ background: "#1a0e00", border: `1px solid ${C.warning}44`, borderRadius: 3, padding: "10px 14px", margin: "1rem 0 0", fontSize: 12, color: C.warning, fontFamily: "inherit" }} className="anim-fade-in">
            ⚠ No OSINT data returned — configure API keys in{" "}
            <code style={{ color: C.warning, background: "transparent" }}>backend/.env</code>{" "}
            and re-enrich.{" "}
            <span onClick={() => navigate("/settings")} style={{ color: C2, cursor: "pointer", textDecoration: "underline" }}>View settings →</span>
          </div>
        )}
        {lead.error_message && (
          <div style={{ background: "#1a0000", color: C.error, padding: "10px 14px", borderRadius: 3, fontSize: 12, margin: "1rem 0 0", border: `1px solid ${C.error}44`, fontFamily: "inherit" }} className="anim-fade-in">
            ✗ {lead.error_message}
          </div>
        )}
      </div>

      {/* Main grid */}
      <div style={{ flex: 1, padding: "1.5rem 2rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {/* Left column */}
        <div>
          <Section title="Person">
            {hasPersonData ? (
              <>
                <Field label="Name" value={lead.name} />
                <Field label="Title" value={lead.job_title} />
                <Field label="LinkedIn" value={lead.linkedin_url} link={lead.linkedin_url} />
                <Field label="Twitter" value={lead.twitter_url} link={lead.twitter_url} />
                <Field label="GitHub" value={lead.github_url} link={lead.github_url} />
                <Field label="Bio" value={lead.bio} />
                {lead.interests.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    <span style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1, textTransform: "uppercase", fontFamily: "inherit" }}>Interests </span>
                    <span style={{ fontSize: 12, color: C.textSub, fontFamily: "inherit" }}>{lead.interests.join(" · ")}</span>
                  </div>
                )}
              </>
            ) : <EmptyState message={isDone ? "No person data found." : "Not yet enriched."} />}
          </Section>

          <Section title="Company">
            {hasCompanyData ? (
              <>
                <Field label="Name" value={lead.company_name} />
                <Field label="Industry" value={lead.company_industry} />
                <Field label="Size" value={lead.company_size} />
                <Field label="Website" value={lead.company_website} link={lead.company_website} />
                <Field label="About" value={lead.company_description} />
              </>
            ) : <EmptyState message={isDone ? "No company data found." : "Not yet enriched."} />}
          </Section>

          {lead.recent_posts.length > 0 && (
            <Section title="Recent Activity">
              {lead.recent_posts.map((p, i) => (
                <div key={i} style={{ fontSize: 12, color: C.textSub, marginBottom: 8, paddingLeft: 10, borderLeft: `2px solid ${G}44`, lineHeight: 1.5, fontFamily: "inherit" }}>
                  {p}
                </div>
              ))}
            </Section>
          )}

          {lead.recent_news.length > 0 && (
            <Section title="Intel Feed">
              {lead.recent_news.map((n, i) => (
                <div key={i} style={{ fontSize: 12, color: C.textSub, marginBottom: 8, paddingLeft: 10, borderLeft: `2px solid ${C2}44`, lineHeight: 1.5, fontFamily: "inherit" }}>
                  {n}
                </div>
              ))}
            </Section>
          )}

          {isDone && (hasRawAnalysis
            ? <OsintAnalysis rawAnalysis={lead.raw_analysis} />
            : <Section title="OSINT Analysis"><EmptyState message='No source data. Click Re-Enrich to run the pipeline.' /></Section>
          )}

          {lead.enrichment_sources.length > 0 && (
            <p style={{ fontSize: 10, color: C.textMuted, marginTop: 4, letterSpacing: 0.5, fontFamily: "inherit" }}>
              sources: {lead.enrichment_sources.join(" · ")}
            </p>
          )}
        </div>

        {/* Right column */}
        <div>
          {isDone && (
            <Section title="Generate Outreach">
              {hasNoData && (
                <div style={{ fontSize: 11, color: C.warning, marginBottom: 12, padding: "8px", background: "#1a0e00", borderRadius: 3, border: `1px solid ${C.warning}33`, fontFamily: "inherit" }}>
                  ⚠ No intel found — output will be generic. Re-enrich with API keys first.
                </div>
              )}
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 10, color: C.textMuted, letterSpacing: 1.5, marginBottom: 8, fontFamily: "inherit" }}>OUTPUT TYPES</div>
                <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                  {[
                    { key: "email", label: "Cold Email" },
                    { key: "call_script", label: "Call Script" },
                    { key: "linkedin_msg", label: "LinkedIn" },
                  ].map(({ key, label }) => (
                    <label key={key} style={{ fontSize: 12, display: "flex", gap: 6, alignItems: "center", color: C.textSub, cursor: "pointer", fontFamily: "inherit" }}>
                      <input
                        type="checkbox"
                        checked={outputTypes.includes(key)}
                        onChange={e => setOutputTypes(prev => e.target.checked ? [...prev, key] : prev.filter(t => t !== key))}
                        style={{ accentColor: G }}
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>
              <ProductForm onGenerate={handleGenerate} loading={generating} />
              {genError && <p style={{ color: C.error, fontSize: 12, marginTop: 8, fontFamily: "inherit" }}>✗ {genError}</p>}
            </Section>
          )}

          {hasOutputs && (
            <Section title="Generated Outreach">
              {lead.generated_email && <OutputCard title="Cold Email" content={lead.generated_email} />}
              {lead.generated_call_script && <OutputCard title="Call Script" content={lead.generated_call_script} />}
              {lead.generated_linkedin_msg && <OutputCard title="LinkedIn Message" content={lead.generated_linkedin_msg} />}
            </Section>
          )}
        </div>
      </div>
    </div>
  );
}
