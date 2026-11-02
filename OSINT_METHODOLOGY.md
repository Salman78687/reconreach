# OSINT Methodology — How Lead Enrichment Works

This document explains exactly how the platform collects intelligence on a lead, what each source contributes, how the data is merged, and how it flows into the LLM to generate personalized outreach.

---

## Overview

The goal of OSINT here is not surveillance — it is **context gathering**. When a cold email opens with a specific reference to something the recipient published, built, or was quoted on, it signals genuine interest and dramatically increases reply rates. The pipeline automates what a skilled sales researcher would do manually in 20–30 minutes per lead.

Every source runs **concurrently** using Python `asyncio.gather`, so a full enrichment cycle for one lead typically completes in 3–8 seconds even when hitting multiple external APIs in parallel.

---

## Plan Tiers

The pipeline has two modes controlled by `PLAN_TIER` in `backend/.env`:

| Tier | Sources | API Keys Needed |
|------|---------|----------------|
| `free` | GitHub, Gravatar, WHOIS, EmailRep.io, LinkedIn scraper, HIBP*, Clearbit*, Snov.io* | None required (* = runs if key set) |
| `paid` | Everything in Free + Hunter.io, Apollo.io, Google CSE, Twitter/X | Respective API keys |

---

## Email Lead Pipeline

**File:** `backend/osint/email_enricher.py`

### Step 0 — Validation and Domain Extraction

The email is normalized using the `email-validator` library. The domain is extracted:

```
john.doe@acmecorp.com  →  domain = "acmecorp.com"
```

The domain is used for company lookups (WHOIS, Hunter domain search). The full email is used for person lookups.

---

### Step 1 — Wave 1: All sources run concurrently

Up to 7 sources fire simultaneously via `asyncio.gather`. Which ones run depends on the plan tier and which optional keys are configured.

#### 1a. Gravatar — Free, no key required
**File:** `backend/osint/sources/gravatar.py`
**API:** `GET https://www.gravatar.com/{md5(email)}.json`

Gravatar stores a public profile linked to an email's MD5 hash. Many people have one without knowing. Returns:
- Display name and bio
- Avatar URL
- Linked social profiles (LinkedIn, GitHub, Twitter URLs if user added them)

Zero setup — always runs on both free and paid plans.

#### 1b. WHOIS — Free, no key required
**File:** `backend/osint/sources/whois_lookup.py`
**Library:** `python-whois` (queries public WHOIS servers, fully offline)

For company emails, the domain's WHOIS registration often reveals:
- Organization/registrant name
- Country
- Registrar
- Domain creation date

Most useful for company emails (`@acmecorp.com`). Returns nothing useful for Gmail/Yahoo/etc.

#### 1c. EmailRep.io — Free, no key required (100 req/day)
**File:** `backend/osint/sources/emailrep.py`
**API:** `GET https://emailrep.io/{email}`

Returns reputation signals about the email address:
- Reputation score: `high` / `medium` / `low` / `none`
- Whether the email has appeared in data breaches
- Associated social profiles detected
- Domain reputation
- Disposable/free provider flags

No API key needed for basic use. Useful as a trust signal before investing enrichment credits on a lead.

#### 1d. GitHub API — Free (token optional, increases rate limit)
**File:** `backend/osint/sources/github.py`
**API:** `GET https://api.github.com/search/commits` and `/search/users`

Two lookup strategies in sequence:

**Strategy 1 — Commit search by email:**
```
GET /search/commits?q=author-email:{email}
```
GitHub indexes the author email on every public commit. If the person has pushed commits with this email, the search returns their GitHub username.

**Strategy 2 — User search fallback:**
```
GET /search/users?q={email}+in:email
```
Some users make their email public on their profile.

Once a username is found, fetches:
- Name, bio, company
- Top 5 starred repos → extracts programming languages and topics as `interests`

**Note:** Returns empty for most leads — only works if the person has public GitHub activity linked to that exact email address, or has made their email public on their profile.

#### 1e. Have I Been Pwned (HIBP) — Optional key (~$5/mo)
**File:** `backend/osint/sources/hibp.py`
**API:** `GET https://haveibeenpwned.com/api/v3/breachedaccount/{email}`
**Env var:** `HIBP_API_KEY`

Returns a summary of every known data breach the email appeared in:
- Breach count
- Breach names and dates
- Categories of exposed data (passwords, phone numbers, addresses, etc.)

Skipped if `HIBP_API_KEY` is not set. When configured, runs on both free and paid plans.

#### 1f. Clearbit — Optional key (free trial available)
**File:** `backend/osint/sources/clearbit.py`
**API:** `GET https://person.clearbit.com/v2/combined/find?email={email}`
**Env var:** `CLEARBIT_API_KEY`

Returns a combined person + company profile:
- Full name, job title, bio
- LinkedIn, Twitter, GitHub handles
- Company name, industry, size, website, description

Skipped if `CLEARBIT_API_KEY` is not set.

#### 1g. Snov.io — Optional key (50 free credits/mo)
**File:** `backend/osint/sources/snov.py`
**API:** OAuth2 + `/email-verifier` + `/get-profile-by-email`
**Env vars:** `SNOV_CLIENT_ID`, `SNOV_CLIENT_SECRET`

Two calls: email verification (valid/invalid/SMTP check) + profile lookup. Returns:
- Verification status and SMTP validity
- Name, job title, company, LinkedIn URL

Consumes 2 credits per lead. Skipped if credentials are not set.

---

### Step 2 — Paid Wave 1 Sources (PLAN_TIER=paid only)

These fire concurrently alongside the free sources when `PLAN_TIER=paid`:

#### Hunter.io — Domain Search
**File:** `backend/osint/sources/hunter.py` → `get_company_from_domain(domain)`
**API:** `GET https://api.hunter.io/v2/domain-search`

Returns company name, industry, headcount range, LinkedIn/Twitter URLs from the email domain.

#### Hunter.io — Email Enrichment
**API:** `GET https://api.hunter.io/v2/email-enrichment`

Returns person name, job title, LinkedIn URL, Twitter handle, bio from the full email address.

#### Apollo.io — Person Match
**File:** `backend/osint/sources/apollo.py` → `enrich_person(email)`
**API:** `POST https://api.apollo.io/v1/people/match`

Returns full professional profile: name, title, seniority, LinkedIn URL, city, company name, industry, employee count, description.

---

### Step 3 — Data Merge with Priority

After Wave 1 completes, results are merged into a single `EnrichedProfile` dataclass. Priority order for conflicting values:

```
Clearbit > Apollo > Hunter/email > Gravatar > GitHub   (person fields)
Hunter/domain > Apollo > WHOIS > Clearbit              (company fields)
```

Fields are filled with an "or" pattern — the first non-null value wins and is never overwritten.

---

### Step 4 — Wave 2: Dependent Sources (run after Wave 1)

These need the name/company resolved from Wave 1:

#### LinkedIn Profile Scrape — Free (fragile)
**File:** `backend/osint/sources/linkedin.py`

If a LinkedIn URL was found in Wave 1, attempts to fetch the public profile page with a User-Agent that identifies this tool. Parses the `<meta name="description">` tag for headline and summary. LinkedIn increasingly serves login walls — works inconsistently.

If no LinkedIn URL was found and the person's name is known, tries a Google dork first:
```
site:linkedin.com/in "John Doe" "Acme Corp"
```

#### Google News — Person (PLAN_TIER=paid only)
**File:** `backend/osint/sources/google_search.py` → `get_recent_news(name, company)`

Searches Google Custom Search for recent mentions of the person. Returns up to 5 snippets — these are direct personalization hooks for the LLM.

#### Google News — Company (PLAN_TIER=paid only)
```
get_company_news(company_name)
```
Separate search for company news (funding, launches, executive changes).

---

### Step 5 — Twitter/X Activity (PLAN_TIER=paid only)
**File:** `backend/osint/sources/twitter.py`

If a Twitter URL was found in Wave 1, fetches up to 10 recent original tweets (excludes retweets and replies). The 5 most recent are stored as `recent_posts` — the highest-signal personalization data available.

---

### Step 6 — Enrichment Score

After all sources are merged, a score from 0–100 is computed based on how many profile fields were populated:

```python
scored_fields = [name, job_title, linkedin_url, twitter_url, github_url, bio,
                 company_name, company_industry, company_size, company_website,
                 company_description]
list_fields   = [recent_posts, interests, recent_news]

score = round((filled_count / total_count) * 100)
```

A score of 0 means no source returned any data. 60–80% is typical with 2–3 sources contributing. 100% requires all fields populated.

---

## Phone Lead Pipeline

**File:** `backend/osint/phone_enricher.py`

Phone numbers are harder to enrich — there is no equivalent of the email-to-person database ecosystem.

### Step 1 — Number Parsing (free, offline)
The `phonenumbers` Python library validates the number and extracts:
- International format
- Country and carrier
- Line type: mobile / landline / VoIP / toll-free

### Step 2 — PhoneInfoga CLI (free if installed)
Invoked as a subprocess if the `phoneinfoga` CLI is installed:
```bash
phoneinfoga scan -n {phone} --output json
```

### Step 3 — Google Reverse Lookup
Searches the phone number in quotes to find business listings, LinkedIn profiles, or directories. If a LinkedIn URL is found, the LinkedIn scraper is invoked.

---

## Raw Analysis Storage

Every source result — success, empty, error, or skipped — is stored in the `raw_analysis` JSON field on the lead record:

```json
{
  "gravatar":           { "status": "success", "data": { "name": "John Doe", ... } },
  "whois":              { "status": "success", "data": { "org": "Acme Corp", ... } },
  "emailrep.io":        { "status": "empty",   "data": {} },
  "github":             { "status": "empty",   "data": {} },
  "hibp":               { "status": "success", "data": { "breached": true, "breach_count": 3, ... } },
  "clearbit":           { "status": "skipped", "data": {}, "note": "CLEARBIT_API_KEY not configured" },
  "snov.io":            { "status": "skipped", "data": {}, "note": "SNOV_CLIENT_ID/SECRET not configured" },
  "hunter.io/domain":   { "status": "skipped", "data": {}, "note": "paid plan only" },
  "hunter.io/email":    { "status": "skipped", "data": {}, "note": "paid plan only" },
  "apollo.io":          { "status": "skipped", "data": {}, "note": "paid plan only" },
  "linkedin":           { "status": "empty",   "data": {} },
  "google_news/person": { "status": "skipped", "data": {}, "note": "paid plan only" },
  "google_news/company":{ "status": "skipped", "data": {}, "note": "paid plan only" },
  "twitter/x":          { "status": "skipped", "data": {}, "note": "paid plan only" }
}
```

| Status | Meaning |
|--------|---------|
| `success` | Source returned data that was used |
| `empty` | Source returned a valid response but found nothing |
| `error` | An exception occurred (network timeout, API error, bug) |
| `skipped` | Source not queried — key not configured, or paid-plan-only |

This is displayed in the UI as the **OSINT Analysis** section — collapsible per-source rows with expandable raw JSON.

---

## From OSINT Data to LLM Prompt

**File:** `backend/llm/prompts.py`

The enriched profile is serialized into a structured text block:

```
Name: John Doe, VP Engineering at Acme Corp
Industry: SaaS / Developer Tools
Bio: Building distributed systems. Previously at Stripe.
Recent activity / posts:
  - "Thinking a lot about developer experience lately"
  - "We just open-sourced our internal CLI framework"
Interests: Python, Go, cli, devops
Recent news:
  - Acme Corp raises $40M Series B to expand API platform
```

This is combined with the seller's product description and passed to one of three system prompts:

- **Cold email** — under 150 words, opens with a specific hook from the enriched data
- **Call script** — 5-part structure: pattern interrupt → permission → bridge → qualifying question → CTA
- **LinkedIn message** — under 80 words, observation-first, no emojis, human tone

**LLM:** All generation uses a self-hosted OpenAI-compatible API (`backend/llm/client.py`). Configure the endpoint, key, and model in `backend/.env`:

```env
LLM_API_BASE=http://your-server:8000/v1
LLM_API_KEY=EMPTY
LLM_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct
```

Works with any OpenAI-compatible backend: vLLM, Ollama, LM Studio, or the real OpenAI API.

---

## Data Flow Summary

```
Email/Phone Lead
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Wave 1 (all concurrent)                                     │
│                                                              │
│  FREE ALWAYS:  Gravatar · WHOIS · EmailRep · GitHub         │
│  FREE IF KEY:  HIBP · Clearbit · Snov.io                    │
│  PAID ONLY:    Hunter/domain · Hunter/email · Apollo         │
└──────────────────────────┬───────────────────────────────────┘
                           │ merge + resolve name/company
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Wave 2 (concurrent, uses Wave 1 output)                     │
│  LinkedIn scrape (free)                                      │
│  Google News/person + Google News/company (paid only)        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
              Twitter/X (paid only, if URL found)
                           │
                           ▼
              EnrichedProfile + raw_analysis
                           │
                 ┌─────────┴─────────┐
                 │                   │
              Stored in DB      LLM prompt
                              (self-hosted Llama)
                                     │
                          ┌──────────┼──────────┐
                       Email    Call Script   LinkedIn Msg
```

---

## Limitations and Ethical Notes

- **All data collected is publicly available.** No passwords, no private accounts, no data breaches exploited. Every source used is either a public API, a public search index, or a public-facing profile page.
- **GitHub hits are rare** — only works if the person has public commits linked to that exact email, or has made their email public on their profile.
- **LinkedIn scraping is fragile.** LinkedIn actively blocks scrapers. The implementation captures what it can from public pages but will often return empty results. A production system at scale should use Proxycurl.
- **HIBP** requires a paid API key (~$5/mo). It only reports whether an email appeared in known public breaches — it does not expose breach data itself.
- **Hunter.io and Apollo.io free tiers** are 25–50 credits/month respectively. For bulk enrichment, paid plans are required.
- **Phone enrichment is significantly weaker** than email enrichment. Phone number → person identity is a hard problem without paid reverse-lookup services.
- **This tool is for B2B outreach only.** Enriching personal contacts or using the output to harass, stalk, or spam people violates the terms of every API used and may violate GDPR, CAN-SPAM, and other applicable laws.
