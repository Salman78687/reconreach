# OSINT Cold Outreach Platform

Automatically enrich leads (emails or phone numbers) using passive OSINT intelligence, then generate personalized cold emails, call scripts, and LinkedIn messages using a self-hosted LLM.

---

## What it does

1. You provide a list of leads — email addresses or phone numbers (via CSV upload or single input)
2. The platform concurrently queries multiple OSINT sources to build a profile on each person
3. You describe your product/service and click **Generate Outreach**
4. A self-hosted Llama model writes personalized outreach using the enriched profile as context

---

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- Git

### 1 — Clone

```bash
git clone https://github.com/salman17-git/Osint-cold-call.git
cd Osint-cold-call
```

### 2 — Configure environment

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in the values you want. The only required ones to get started are:

```env
# Required: your self-hosted LLM endpoint
LLM_API_BASE=http://your-llm-server:8000/v1
LLM_API_KEY=EMPTY
LLM_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct

# Optional: set to "paid" to enable Hunter/Apollo/Google/Twitter sources
PLAN_TIER=free
```

Everything else is optional — the platform works on the free plan with no paid API keys.

### 3 — Run

```bash
sudo docker compose up --build -d
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API docs:** http://localhost:8000/docs

---

## OSINT Plans

### Free Plan (`PLAN_TIER=free`)

No paid API keys required. Runs automatically:

| Source | What it returns |
|--------|----------------|
| **GitHub API** | Developer profile, languages, interests from repos |
| **Gravatar** | Name, bio, linked social profiles from email hash |
| **WHOIS** | Company/org name from email domain |
| **EmailRep.io** | Reputation score, breach flags, deliverability |
| **LinkedIn scraper** | Profile bio/headline (best-effort, often blocked) |
| **phonenumbers** | Phone validation, country, carrier, line type (offline) |
| **PhoneInfoga** | Extended phone metadata (if CLI installed) |

Optional free-tier extras (add key to `.env` to enable):

| Source | Key | Cost |
|--------|-----|------|
| **Have I Been Pwned** | `HIBP_API_KEY` | ~$5.29/mo (Core 1 plan) |
| **Clearbit** | `CLEARBIT_API_KEY` | Free trial |
| **Snov.io** | `SNOV_CLIENT_ID` + `SNOV_CLIENT_SECRET` | 50 free/mo |

### Paid Plan (`PLAN_TIER=paid`)

Adds on top of the free plan:

| Source | Key | Free Tier |
|--------|-----|-----------|
| **Hunter.io** | `HUNTER_API_KEY` | 25 req/mo |
| **Apollo.io** | `APOLLO_API_KEY` | 50 credits/mo |
| **Google Custom Search** | `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID` | 100 req/day |
| **Twitter/X** | `TWITTER_BEARER_TOKEN` | Basic tier |
| **NumVerify** | `NUMVERIFY_API_KEY` | 250 req/mo |

---

## LLM Configuration

The platform uses an OpenAI-compatible API, so it works with any self-hosted model (vLLM, Ollama, LM Studio, etc.) or with the real OpenAI API.

```env
LLM_API_BASE=http://192.168.1.100:8000/v1   # your server
LLM_API_KEY=EMPTY                            # use EMPTY for local, or a real key
LLM_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct
```

To use OpenAI instead:
```env
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

---

## Usage

1. Open http://localhost:3000
2. Add a lead — type an email or phone number and click **[ SCAN TARGET ]**, or upload a CSV with a column named `email`, `phone`, or `lead`
3. Enrichment starts automatically. Watch the status badges update in real time
4. Click any lead to open its detail page
5. In the **Generate Outreach** panel, describe what you're selling and click **[ GENERATE OUTREACH ]**
6. Copy the generated email, call script, or LinkedIn message

---

## Architecture

```
browser → nginx (port 3000)
               ↓
          React + Vite SPA
               ↓
     FastAPI backend (port 8000)
          ↙         ↘
   SQLite DB     OSINT pipeline
                 (asyncio.gather)
                      ↓
              7+ concurrent sources
                      ↓
              EnrichedProfile → LLM
```

- **Backend:** Python 3.12, FastAPI, SQLAlchemy (SQLite), asyncio
- **Frontend:** React 19, TypeScript, Vite, react-router-dom
- **Deployment:** Docker Compose (multi-stage builds, nginx for frontend)
- **Database:** SQLite with named Docker volume (persists across restarts)

---

## Project Structure

```
├── backend/
│   ├── api/routes/          # FastAPI routes (leads, enrichment, generation)
│   ├── core/                # Config (pydantic-settings), database
│   ├── llm/                 # LLM client + prompt templates + generators
│   ├── models/              # SQLAlchemy Lead model + EnrichedProfile dataclass
│   ├── osint/
│   │   ├── email_enricher.py   # Two-wave concurrent email pipeline
│   │   ├── phone_enricher.py   # Phone number pipeline
│   │   └── sources/            # One file per OSINT source
│   ├── .env.example         # All configurable env vars
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, LeadDetail, Settings
│       ├── components/      # Reusable UI components
│       └── api/client.ts    # Typed Axios API client
├── docker-compose.yml
└── OSINT_METHODOLOGY.md     # Deep-dive into how each source works
```

---

## Environment Variables Reference

Copy `backend/.env.example` to `backend/.env`:

```env
# Plan: "free" or "paid"
PLAN_TIER=free

# Self-hosted LLM
LLM_API_BASE=http://YOUR_LLM_HOST:8000/v1
LLM_API_KEY=EMPTY
LLM_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct

# Free-tier optional
HIBP_API_KEY=
CLEARBIT_API_KEY=
SNOV_CLIENT_ID=
SNOV_CLIENT_SECRET=

# Paid sources (PLAN_TIER=paid)
HUNTER_API_KEY=
APOLLO_API_KEY=
GITHUB_TOKEN=
GOOGLE_CSE_API_KEY=
GOOGLE_CSE_ID=
TWITTER_BEARER_TOKEN=
NUMVERIFY_API_KEY=

# Database (auto-configured in Docker)
DATABASE_URL=sqlite:///./osint_cold_call.db
```

---

## Notes

- `.env` is **not committed** — it contains secrets. Only `.env.example` is in the repo.
- The SQLite database persists via a Docker named volume (`db_data`). Your leads survive container restarts.
- All OSINT sources run concurrently using `asyncio.gather`. A full enrichment cycle takes 3–8 seconds.
- LinkedIn scraping is best-effort — LinkedIn blocks most scrapers. For reliable LinkedIn data at scale, use Proxycurl.
- This tool is intended for B2B outreach only. All data collected is publicly available.
