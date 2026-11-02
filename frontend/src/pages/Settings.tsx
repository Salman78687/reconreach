import { useNavigate } from "react-router-dom";

const G = "#00ff9d";
const C2 = "#00c4f0";
const C = {
  bg: "#060b14", card: "#0d1520", border: "#1a2a3a",
  text: "#c8fce0", textSub: "#5a9e7a", textMuted: "#2d5a44",
  error: "#ff4040", warning: "#ffaa00",
};

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code style={{ background: "#030608", padding: "2px 6px", borderRadius: 2, fontSize: 11, color: G, border: `1px solid #1a2a3a`, fontFamily: "inherit" }}>
      {children}
    </code>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ border: `1px solid ${C.border}`, borderRadius: 4, background: C.card, marginBottom: "1.5rem", overflow: "hidden" }} className="anim-fade-up">
      <div style={{ padding: "10px 16px", borderBottom: `1px solid ${C.border}`, background: "#0a1520" }}>
        <span style={{ fontSize: 10, color: G, letterSpacing: 2, fontWeight: 700, fontFamily: "inherit" }}>{title}</span>
      </div>
      <div style={{ padding: "1.25rem 1.5rem" }}>{children}</div>
    </div>
  );
}

function Table({ cols, rows }: { cols: string[]; rows: React.ReactNode[][] }) {
  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
      <thead>
        <tr style={{ borderBottom: `1px solid ${C.border}` }}>
          {cols.map(c => (
            <th key={c} style={{ textAlign: "left", padding: "6px 10px", color: C.textMuted, fontWeight: 700, fontSize: 10, letterSpacing: 1.5, textTransform: "uppercase", fontFamily: "inherit" }}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} style={{ borderBottom: `1px solid ${C.border}` }}>
            {row.map((cell, j) => (
              <td key={j} style={{ padding: "10px 10px", fontFamily: "inherit" }}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Settings() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: "100vh" }}>
      {/* Top bar */}
      <div style={{ borderBottom: `1px solid ${C.border}`, background: "#0a1520", padding: "0 2rem", display: "flex", alignItems: "center", height: 52 }}>
        <button
          onClick={() => navigate("/")}
          style={{ background: "none", border: "none", color: C.textSub, cursor: "pointer", fontSize: 11, fontFamily: "inherit", letterSpacing: 1, padding: 0 }}
          onMouseEnter={e => ((e.currentTarget as HTMLElement).style.color = G)}
          onMouseLeave={e => ((e.currentTarget as HTMLElement).style.color = C.textSub)}
        >
          ← TARGETS
        </button>
        <span style={{ color: C.border, margin: "0 16px" }}>|</span>
        <span style={{ fontSize: 10, color: G, letterSpacing: 2, fontWeight: 700, fontFamily: "inherit" }}>SYSTEM SETTINGS</span>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem" }}>
        <div style={{ marginBottom: "2rem" }}>
          <h1 style={{ margin: 0, fontSize: 22, color: G, fontWeight: 700, letterSpacing: 2, fontFamily: "inherit", textShadow: `0 0 20px ${G}44` }}>
            SETTINGS & CONFIGURATION
          </h1>
          <p style={{ margin: "8px 0 0", color: C.textMuted, fontSize: 12, fontFamily: "inherit" }}>
            All configuration via <Code>backend/.env</Code> — copy from <Code>backend/.env.example</Code>
          </p>
        </div>

        {/* Plan Tier */}
        <Card title="PLAN TIER">
          <p style={{ margin: "0 0 1rem", color: C.textSub, fontSize: 12, lineHeight: 1.7, fontFamily: "inherit" }}>
            Set <Code>PLAN_TIER=free</Code> or <Code>PLAN_TIER=paid</Code> to control which OSINT sources activate.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            {[
              {
                tier: "FREE", color: G, env: "PLAN_TIER=free",
                sources: ["GitHub API", "Gravatar", "WHOIS lookup", "EmailRep.io", "LinkedIn scraper", "phonenumbers (offline)", "PhoneInfoga CLI", "+ HIBP / Clearbit / Snov (if key set)"],
              },
              {
                tier: "PAID", color: C2, env: "PLAN_TIER=paid",
                sources: ["Everything in Free, plus:", "Hunter.io (domain + email)", "Apollo.io (person profile)", "Google Custom Search", "Twitter/X API"],
              },
            ].map(({ tier, color, env, sources }) => (
              <div key={tier} style={{ background: "#060b14", border: `1px solid ${color}33`, borderRadius: 3, padding: "1rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 10, fontWeight: 700, color, background: `${color}15`, padding: "2px 8px", borderRadius: 2, border: `1px solid ${color}44`, letterSpacing: 1, fontFamily: "inherit" }}>
                    {tier}
                  </span>
                  <Code>{env}</Code>
                </div>
                <ul style={{ margin: 0, padding: "0 0 0 14px", fontSize: 11, color: C.textSub, lineHeight: 2, fontFamily: "inherit" }}>
                  {sources.map(s => <li key={s}>{s}</li>)}
                </ul>
              </div>
            ))}
          </div>
        </Card>

        {/* LLM Config */}
        <Card title="LLM CONFIGURATION">
          <p style={{ margin: "0 0 1rem", color: C.textSub, fontSize: 12, fontFamily: "inherit" }}>
            Works with any OpenAI-compatible API: Ollama, vLLM, LM Studio or a hosted provider. Configure in <Code>backend/.env</Code>.
          </p>
          <Table
            cols={["Env Var", "Default", "Purpose"]}
            rows={[
              [<Code>LLM_API_BASE</Code>, <Code>http://localhost:11434/v1</Code>, <span style={{ color: C.textSub }}>API endpoint</span>],
              [<Code>LLM_API_KEY</Code>, <Code>EMPTY</Code>, <span style={{ color: C.textSub }}>API key (EMPTY for local)</span>],
              [<Code>LLM_MODEL</Code>, <span style={{ color: C.textSub, fontSize: 11 }}>llama3.1</span>, <span style={{ color: C.textSub }}>Model name</span>],
            ]}
          />
        </Card>

        {/* Free optional keys */}
        <Card title="FREE-TIER OPTIONAL SOURCES">
          <p style={{ margin: "0 0 1rem", color: C.textSub, fontSize: 12, fontFamily: "inherit" }}>
            Run on the free plan when key is configured. Skipped if key is not set.
          </p>
          <Table
            cols={["Service", "Provides", "Env Var", "Cost"]}
            rows={[
              [
                <span style={{ color: C.text, fontWeight: 700 }}>Have I Been Pwned</span>,
                <span style={{ color: C.textSub }}>Breach history</span>,
                <Code>HIBP_API_KEY</Code>,
                <span style={{ color: C.warning }}>~$3.50/mo</span>,
              ],
              [
                <span style={{ color: C.text, fontWeight: 700 }}>Clearbit</span>,
                <span style={{ color: C.textSub }}>Person + company</span>,
                <Code>CLEARBIT_API_KEY</Code>,
                <span style={{ color: C.warning }}>Free trial</span>,
              ],
              [
                <span style={{ color: C.text, fontWeight: 700 }}>Snov.io</span>,
                <span style={{ color: C.textSub }}>Email verify + profile</span>,
                <span><Code>SNOV_CLIENT_ID</Code><br /><Code>SNOV_CLIENT_SECRET</Code></span>,
                <span style={{ color: G }}>50 free/mo</span>,
              ],
            ]}
          />
        </Card>

        {/* Paid keys */}
        <Card title="PAID OSINT SOURCES (PLAN_TIER=paid)">
          <Table
            cols={["Service", "Provides", "Env Var", "Free Tier"]}
            rows={[
              [<span style={{ color: C.text, fontWeight: 700 }}>Hunter.io</span>, <span style={{ color: C.textSub }}>Company + person from email</span>, <Code>HUNTER_API_KEY</Code>, <span style={{ color: G }}>25 req/mo</span>],
              [<span style={{ color: C.text, fontWeight: 700 }}>Apollo.io</span>, <span style={{ color: C.textSub }}>Full person profile</span>, <Code>APOLLO_API_KEY</Code>, <span style={{ color: G }}>50 credits/mo</span>],
              [<span style={{ color: C.text, fontWeight: 700 }}>GitHub</span>, <span style={{ color: C.textSub }}>Dev profile (optional key)</span>, <Code>GITHUB_TOKEN</Code>, <span style={{ color: G }}>5,000 req/hr</span>],
              [<span style={{ color: C.text, fontWeight: 700 }}>Google CSE</span>, <span style={{ color: C.textSub }}>News + LinkedIn discovery</span>, <span><Code>GOOGLE_CSE_API_KEY</Code><br /><Code>GOOGLE_CSE_ID</Code></span>, <span style={{ color: G }}>100 req/day</span>],
              [<span style={{ color: C.text, fontWeight: 700 }}>Twitter/X</span>, <span style={{ color: C.textSub }}>Recent tweets</span>, <Code>TWITTER_BEARER_TOKEN</Code>, <span style={{ color: G }}>Basic tier</span>],
            ]}
          />
        </Card>
      </div>
    </div>
  );
}
