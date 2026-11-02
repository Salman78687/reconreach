# OSINT Cold Outreach Platform

Enrich leads (email addresses or phone numbers) with passive, public OSINT data, then generate personalized cold emails, call scripts and LinkedIn messages with any OpenAI-compatible LLM, self-hosted or cloud.

> **Please read [Responsible use](#responsible-use) before running this against real people.**

---

## What it does

1. You add leads: email addresses or phone numbers, one at a time or as a CSV upload.
2. The platform queries several public OSINT sources concurrently to build a profile of each lead.
3. You describe your product or service and click **Generate Outreach**.
4. An LLM writes personalized outreach using the enriched profile as context.

It works out of the box on the **free plan**: no paid API keys are needed. You only need an LLM endpoint for the generation step.

---

## Quick start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose v2.24 or newer
- Git
- An OpenAI-compatible LLM endpoint (see [LLM configuration](#llm-configuration)): a local server such as Ollama, vLLM or LM Studio, or a hosted API

### 1. Clone

```bash
git clone https://github.com/Salman78687/osint-outreach-platform.git
cd osint-outreach-platform
```

### 2. Configure

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and set your LLM endpoint. This is the only setting you need to get started:

```env
LLM_API_BASE=http://host.docker.internal:11434/v1   # e.g. Ollama running on your machine
LLM_API_KEY=EMPTY
LLM_MODEL=llama3.1
```

Everything else is optional. See the [environment variable reference](#environment-variables).

### 3. Run

```bash
docker compose up --build -d
```

| Service | URL |
|---|---|
| Web app | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

Stop it with `docker compose down`. Your leads are kept in a Docker volume (`db_data`) between runs.

---

## Running without Docker

Requires **Python 3.12+** and **Node.js 20+**.

```bash
./start.sh
```

On the first run it creates a Python virtualenv in `.venv`, installs the backend and frontend dependencies, and copies `backend/.env.example` to `backend/.env`. Then it starts:

- Frontend (Vite dev server): http://localhost:5173
- Backend API: http://localhost:8000 (docs at `/docs`)

<details>
<summary>Manual setup instead of <code>start.sh</code></summary>

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env   # then edit it
cd backend && uvicorn main:app --reload --port 8000

# Frontend (in a second terminal)
cd frontend
npm ci
npm run dev
```

When running without Docker, point `LLM_API_BASE` at `http://localhost:<port>/v1` rather than `host.docker.internal`.

</details>

---

## Usage

1. Open the web app.
2. Add a lead: type an email or phone number and click **[ SCAN TARGET ]**, or upload a CSV with a column named `email`, `phone` or `lead`.
3. Enrichment starts automatically. The status badges update in real time.
4. Click a lead to open its detail page and see what was found.
5. In the **Generate Outreach** panel, describe what you're offering and click **[ GENERATE OUTREACH ]**.
6. Copy the generated email, call script or LinkedIn message.

---

## OSINT plans

Set `PLAN_TIER` in `backend/.env` to `free` (default) or `paid`.

### Free plan (`PLAN_TIER=free`)

No API keys required:

| Source | What it returns |
|---|---|
| **GitHub API** | Developer profile, languages, interests from repos |
| **Gravatar** | Name, bio, linked social profiles from the email hash |
| **WHOIS** | Organization name from the email's domain |
| **EmailRep.io** | Reputation score, breach flags, deliverability |
| **LinkedIn (public page)** | Headline and bio from the public profile page, best-effort and often blocked |
| **phonenumbers** | Phone validation, country, carrier, line type (offline) |
| **PhoneInfoga** | Extended phone metadata, if the `phoneinfoga` CLI is installed |

Optional extras that work on the free plan once their key is set:

| Source | Variable(s) | Pricing |
|---|---|---|
| **GitHub** (higher rate limit) | `GITHUB_TOKEN` | Free: 60 → 5,000 requests/hour |
| **Have I Been Pwned** | `HIBP_API_KEY` | Paid subscription |
| **Clearbit** | `CLEARBIT_API_KEY` | Free trial |
| **Snov.io** | `SNOV_CLIENT_ID`, `SNOV_CLIENT_SECRET` | 50 free credits/month |

### Paid plan (`PLAN_TIER=paid`)

Adds these sources on top of the free plan. Each is skipped if its key is empty:

| Source | Variable(s) | Free tier |
|---|---|---|
| **Hunter.io** | `HUNTER_API_KEY` | 25 requests/month |
| **Apollo.io** | `APOLLO_API_KEY` | 50 credits/month |
| **Google Custom Search** | `GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_ID` | 100 requests/day |
| **Twitter/X** | `TWITTER_BEARER_TOKEN` | Basic tier |

Pricing and free tiers are set by each provider and may change; check their sites. For how each source is queried and combined, see [OSINT_METHODOLOGY.md](OSINT_METHODOLOGY.md).

---

## LLM configuration

The backend talks to any **OpenAI-compatible** chat completions API.

| Setup | `LLM_API_BASE` | `LLM_API_KEY` | `LLM_MODEL` (example) |
|---|---|---|---|
| Ollama on your machine, app in Docker | `http://host.docker.internal:11434/v1` | `EMPTY` | `llama3.1` |
| Ollama, app without Docker | `http://localhost:11434/v1` | `EMPTY` | `llama3.1` |
| vLLM / LM Studio on another server | `http://<server-ip>:8000/v1` | `EMPTY` | the model you serve |
| OpenAI | `https://api.openai.com/v1` | your API key | `gpt-4o-mini` |

Enrichment works without an LLM; only the **Generate Outreach** step needs one.

---

## Environment variables

All backend settings live in `backend/.env` (copied from [`backend/.env.example`](backend/.env.example)). Every variable is optional and has a default.

| Variable | Default | Purpose |
|---|---|---|
| `PLAN_TIER` | `free` | `free` or `paid` (see [OSINT plans](#osint-plans)) |
| `LLM_API_BASE` | `http://localhost:11434/v1` | OpenAI-compatible endpoint (the example file uses `host.docker.internal` for Docker) |
| `LLM_API_KEY` | `EMPTY` | API key for the endpoint (`EMPTY` for most local servers) |
| `LLM_MODEL` | `llama3.1` | Model name sent to the endpoint |
| `GITHUB_TOKEN`, `HIBP_API_KEY`, `CLEARBIT_API_KEY`, `SNOV_CLIENT_ID`, `SNOV_CLIENT_SECRET` | empty | Optional free-plan sources |
| `HUNTER_API_KEY`, `APOLLO_API_KEY`, `GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_ID`, `TWITTER_BEARER_TOKEN` | empty | Paid-plan sources |
| `DATABASE_URL` | `sqlite:///./osint_cold_call.db` | SQLAlchemy URL (Docker sets its own) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated frontend URLs allowed to call the API |

The frontend has one setting, read at build time:

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | The URL the browser uses to reach the backend |

### Hosting on a server

If you open the app from another machine, the browser must be able to reach the backend:

```bash
# On the server, before building:
export VITE_API_BASE_URL=http://<server-address>:8000
echo "CORS_ORIGINS=http://<server-address>:3000" >> backend/.env
docker compose up --build -d
```

The app has **no authentication**. Do not expose it to the public internet as-is; put it behind a VPN or an authenticating reverse proxy.

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

- **Backend:** Python 3.12, FastAPI, SQLAlchemy (SQLite), asyncio, httpx
- **Frontend:** React 19, TypeScript, Vite, react-router-dom
- **Deployment:** Docker Compose (multi-stage frontend build served by nginx)

### Project structure

```
├── backend/
│   ├── api/routes/          # FastAPI routes (leads, enrichment, generation)
│   ├── core/                # Settings (pydantic-settings), database
│   ├── llm/                 # LLM client, prompt templates, generators
│   ├── models/              # SQLAlchemy Lead model, EnrichedProfile
│   ├── osint/
│   │   ├── email_enricher.py   # Two-wave concurrent email pipeline
│   │   ├── phone_enricher.py   # Phone number pipeline
│   │   └── sources/            # One file per OSINT source
│   ├── .env.example         # Every configurable setting
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, LeadDetail, Settings
│       ├── components/      # Reusable UI components
│       └── api/client.ts    # Typed Axios API client
├── docker-compose.yml
├── start.sh                 # Local run without Docker
└── OSINT_METHODOLOGY.md     # How each source works
```

---

## Responsible use

This project is for **legitimate B2B prospecting and research**. It only queries public sources and public APIs, but combining public data about a person and contacting them is still regulated. You are responsible for how you use it:

- **Follow the law where you and your leads are.** This includes data-protection laws such as the GDPR (EU/UK), CCPA (California) and PDPL (Saudi Arabia), and anti-spam laws such as CAN-SPAM, PECR and CASL. Many of these require a lawful basis to process personal data and an easy way to opt out of contact.
- **Respect each source's terms of service and rate limits.** Some sites, including LinkedIn, prohibit automated access. The LinkedIn source is best-effort and can be removed from the pipeline if you can't use it lawfully.
- **Don't use it to harass, stalk, dox or deceive anyone,** or for any purpose other than honest outreach.
- **Store only what you need, and delete it when you're done.** Lead data is kept in the local SQLite database.

The software is provided "as is", without warranty; see the [license](LICENSE).

---

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
