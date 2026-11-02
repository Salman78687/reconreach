# Contributing

Thanks for your interest in improving the OSINT Cold Outreach Platform.

## Getting set up

Follow [Running without Docker](README.md#running-without-docker) in the README. `./start.sh` installs everything and starts both servers with hot reload.

## Making a change

1. Fork the repository and create a branch from `main`.
2. Keep each pull request to one change: a fix, a feature or a refactor.
3. Check your work before opening the PR:
   ```bash
   cd frontend && npm run lint && npm run build
   ```
   and make sure the backend starts (`uvicorn main:app` from `backend/`) and `GET /health` returns `{"status": "ok"}`.
4. Describe what changed and why in the PR description.

## Adding an OSINT source

Each source is one module in `backend/osint/sources/`. A new source should:

- query only **public** data or an official API, and respect the provider's terms of service and rate limits,
- read any API key from `core/config.py` settings (never hard-code keys), add the variable to `backend/.env.example` with a link to where to get it, and skip itself cleanly when the key is empty,
- return a plain `dict` and never raise: return `{}` on failure so one source can't break the pipeline,
- be wired into `osint/email_enricher.py` or `osint/phone_enricher.py`, and documented in the README's [OSINT plans](README.md#osint-plans) and in `OSINT_METHODOLOGY.md`.

## Security

Never commit real API keys, `.env` files or real lead data. If you find a security issue, please open an issue without exploit details and ask for a private contact, rather than posting the details publicly.

## Code of conduct

Be respectful. Contributions that make the tool easier to misuse (for harassment, stalking or deceptive contact) will not be accepted; see [Responsible use](README.md#responsible-use).
