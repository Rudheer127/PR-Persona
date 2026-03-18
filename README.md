# ReviewSense AI

**The AI that judges whether you are qualified to review a PR.**

ReviewSense AI is a GitHub-integrated assistant that evaluates pull request reviews through the lens of social dynamics, cultural health, and reviewer judgement quality — not just code correctness.

## What It Does

- **Persona Simulation** — shows how different team archetypes (Team Lead, Junior Dev, "Burned" Senior) would perceive review comments
- **Reviewer Verdict** — issues VETO / PAUSE / CLEAR based on bias patterns, domain coverage, and confidence calibration
- **Social Health Score** — measures tone, clarity, psychological safety, and engagement balance
- **Tone Rewrites** — suggests friction-reducing alternatives for flagged comments

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React, TypeScript) on Vercel |
| Auth + Database | Supabase (Postgres + Auth + Storage) |
| Analysis Service | Python (FastAPI) |
| LLM | OpenAI API (GPT-4o) |
| VCS | GitHub OAuth + GitHub App |

## Documentation

All design docs live in [`docs/`](./docs/):

| Doc | Contents |
|-----|----------|
| [PRD](docs/01_prd.md) | Product requirements, personas, user stories, scope |
| [Technical Design](docs/02_technical_design.md) | Architecture, data model, scoring algorithms, data flow |
| [Codebase Structure](docs/03_codebase_structure.md) | Folder layouts, naming conventions, module responsibilities |
| [User Flows](docs/04_user_flows.md) | Step-by-step flows for PR Author, Reviewer, Team Lead |
| [Security & Guardrails](docs/05_security_guardrails.md) | Secrets, rate limits, privacy, psychological safety |
| [Coding Standards](docs/06_coding_standards.md) | Conventions, testing, observability, error handling |
| [Phases & Milestones](docs/07_phases_milestones.md) | Roadmap from prototype through enterprise readiness |

## Status

🟡 **Pre-coding design phase** — architecture and requirements defined, implementation not yet started.

## License

Private — not open source.
