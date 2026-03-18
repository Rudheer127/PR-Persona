# ReviewSense AI — Codebase Structure & Conventions

## 1. Monorepo Layout

```
reviewsense-ai/
├── apps/
│   ├── web/                    # Next.js frontend + BFF
│   └── analysis-service/       # Python FastAPI microservice
├── packages/
│   └── shared-types/           # Shared TypeScript type definitions
├── supabase/
│   ├── migrations/             # Timestamped SQL migration files
│   ├── seed.sql                # Development seed data
│   ├── config.toml             # Supabase CLI configuration
│   └── functions/              # Supabase Edge Functions (if any)
├── docs/                       # Design docs, ADRs, runbooks
├── .github/
│   └── workflows/              # CI/CD pipelines
├── .env.example                # Template with all required env vars
├── docker-compose.yml          # Local development stack
├── turbo.json                  # Turborepo config (if using)
└── README.md
```

---

## 2. Next.js Frontend (`apps/web/`)

```
apps/web/
├── src/
│   ├── app/                            # App Router
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── callback/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx              # Dashboard shell (sidebar, nav)
│   │   │   ├── page.tsx                # Home / recent analyses
│   │   │   ├── analyze/
│   │   │   │   └── page.tsx            # PR analysis input + results
│   │   │   ├── history/
│   │   │   │   └── page.tsx            # Analysis history list
│   │   │   ├── team/
│   │   │   │   ├── page.tsx            # Team health dashboard
│   │   │   │   └── settings/page.tsx   # Team norms configuration
│   │   │   └── reviewer/
│   │   │       └── [username]/page.tsx # Reviewer profile + stats
│   │   ├── api/                        # API Routes (BFF)
│   │   │   ├── analyze/route.ts        # POST: initiate analysis
│   │   │   ├── analyses/
│   │   │   │   └── [id]/route.ts       # GET: fetch analysis result
│   │   │   ├── team/
│   │   │   │   ├── health/route.ts     # GET: team health data
│   │   │   │   └── norms/route.ts      # GET/PUT: team norms
│   │   │   └── webhooks/
│   │   │       └── analysis-complete/route.ts  # Callback from FastAPI
│   │   ├── layout.tsx                  # Root layout
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                         # Primitive UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── score-gauge.tsx         # Radial score display
│   │   │   └── ...
│   │   ├── analysis/
│   │   │   ├── pr-input-form.tsx       # URL paste / repo picker
│   │   │   ├── persona-card.tsx        # Single persona reaction
│   │   │   ├── persona-grid.tsx        # Grid of persona cards
│   │   │   ├── verdict-badge.tsx       # VETO/PAUSE/CLEAR badge
│   │   │   ├── verdict-detail.tsx      # Expanded verdict explanation
│   │   │   ├── score-breakdown.tsx     # Score with sub-dimensions
│   │   │   ├── tone-rewrite.tsx        # Original vs rewritten comment
│   │   │   └── analysis-skeleton.tsx   # Loading state
│   │   ├── dashboard/
│   │   │   ├── health-trend-chart.tsx
│   │   │   ├── risk-pr-list.tsx
│   │   │   ├── reviewer-workload.tsx
│   │   │   └── score-summary-card.tsx
│   │   └── layout/
│   │       ├── sidebar.tsx
│   │       ├── header.tsx
│   │       └── footer.tsx
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts               # Browser Supabase client
│   │   │   ├── server.ts               # Server-side Supabase client
│   │   │   └── middleware.ts           # Auth middleware
│   │   ├── analysis-service.ts         # HTTP client for FastAPI
│   │   ├── github.ts                   # GitHub API helpers
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── use-analysis.ts             # Analysis state management
│   │   ├── use-team-health.ts
│   │   └── use-reviewer-stats.ts
│   ├── types/
│   │   ├── analysis.ts                 # Analysis result types
│   │   ├── database.ts                 # Generated Supabase types
│   │   └── api.ts                      # API request/response types
│   └── config/
│       └── constants.ts
├── public/
├── next.config.ts
├── package.json
├── tsconfig.json
└── tailwind.config.ts                  # Only if Tailwind is chosen
```

### Key Conventions (Frontend)
- **Server Components by default** — use `'use client'` only when needed
- **API Routes as BFF** — all external service calls proxied through API routes (no direct FastAPI calls from browser)
- **Supabase types auto-generated** — run `supabase gen types typescript` to produce `types/database.ts`
- **Component naming** — PascalCase files, feature-grouped folders
- **Error boundaries** — each route group has an `error.tsx` for graceful degradation

---

## 3. Python FastAPI Service (`apps/analysis-service/`)

```
apps/analysis-service/
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI app factory + startup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                     # Dependency injection providers
│   │   ├── middleware.py               # Auth, CORS, rate limiting, logging
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── analyze.py              # POST /analyze
│   │       ├── health.py               # GET /health
│   │       └── webhooks.py             # Internal callbacks
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                   # Settings (pydantic-settings)
│   │   ├── security.py                 # API key validation, JWT verify
│   │   ├── exceptions.py              # Custom exception hierarchy
│   │   ├── logging.py                 # Structured logging setup
│   │   └── rate_limiter.py            # Token bucket / sliding window
│   ├── models/
│   │   ├── __init__.py
│   │   ├── analysis.py                # SQLAlchemy / Supabase ORM models
│   │   ├── reviewer.py
│   │   └── enums.py                   # Verdict, Severity, etc.
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── pr.py                      # AnalyzablePR, PRMetadata
│   │   ├── analysis.py                # AnalysisRequest, AnalysisResult
│   │   ├── persona.py                 # PersonaReaction, PersonaConfig
│   │   ├── verdict.py                 # ReviewerVerdict, Flag
│   │   ├── scores.py                  # SocialHealthScore, JudgementScore
│   │   └── github.py                  # GitHub API DTOs
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_orchestrator.py   # Coordinates the 3 pipelines
│   │   ├── persona_analyzer.py        # Persona reaction pipeline
│   │   ├── judgement_analyzer.py      # Reviewer judgement pipeline
│   │   ├── social_health_scorer.py    # Social health scoring
│   │   ├── tone_rewriter.py           # Friction comment rewriting
│   │   ├── verdict_calculator.py      # Deterministic verdict from flags
│   │   └── reviewer_stats_updater.py  # Rolling aggregate updates
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── analysis_repo.py           # CRUD for pr_analyses
│   │   ├── reviewer_stats_repo.py     # CRUD for reviewer_stats
│   │   ├── pr_repo.py                 # CRUD for pull_requests
│   │   └── norms_repo.py             # CRUD for team_norms
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # LLMClient protocol (abstract)
│   │   │   ├── openai_client.py       # OpenAI implementation
│   │   │   └── mock_client.py         # Deterministic mock for testing
│   │   ├── github_client.py           # GitHub API wrapper
│   │   └── supabase_client.py         # Supabase Python client wrapper
│   ├── prompts/
│   │   ├── persona_reaction.py        # Prompt template + version
│   │   ├── tone_analysis.py
│   │   ├── bias_detection.py
│   │   ├── tone_rewrite.py
│   │   └── _base.py                   # Base prompt template class
│   └── utils/
│       ├── __init__.py
│       ├── diff_parser.py             # Parse GitHub diff stats
│       ├── file_classifier.py         # Categorize files (security, infra, etc.)
│       └── correlation.py             # Correlation ID management
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── unit/
│   │   ├── test_verdict_calculator.py
│   │   ├── test_social_health_scorer.py
│   │   ├── test_file_classifier.py
│   │   └── test_diff_parser.py
│   ├── integration/
│   │   ├── test_github_client.py
│   │   ├── test_analysis_repo.py
│   │   └── test_analysis_orchestrator.py
│   └── fixtures/
│       ├── sample_pr.json             # Realistic PR payloads
│       └── sample_comments.json
├── alembic/                            # DB migrations (if not using Supabase CLI)
│   ├── versions/
│   └── env.py
├── pyproject.toml                      # Dependencies, tooling config
├── Dockerfile
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

### Key Conventions (Python Service)

| Area | Convention |
|------|-----------|
| **Config** | `pydantic-settings` with `.env` files; all secrets from env vars, never defaults |
| **Schemas** | Pydantic v2 `BaseModel` for all API boundaries; strict mode enabled |
| **Models vs Schemas** | `models/` = database representation; `schemas/` = API/domain transfer objects |
| **Services** | Pure business logic; no HTTP or DB concerns; receive dependencies via constructor injection |
| **Repositories** | Data access layer; return domain models, accept domain types |
| **Clients** | External service wrappers (LLM, GitHub, Supabase); hide transport details |
| **Prompts** | Versioned templates with `PROMPT_VERSION` constant; include few-shot examples |
| **Error handling** | Custom exceptions in `core/exceptions.py`; mapped to HTTP responses in `api/middleware.py` |
| **Logging** | Structured JSON logs via `structlog`; correlation ID on every request |
| **Testing** | `pytest` + `pytest-asyncio`; mock LLM client for unit tests; real Supabase for integration |

---

## 4. Supabase Configuration (`supabase/`)

```
supabase/
├── config.toml                 # Project settings, auth config
├── migrations/
│   ├── 20260101000000_initial_schema.sql
│   ├── 20260101000001_rls_policies.sql
│   ├── 20260101000002_indexes.sql
│   └── ...                     # Timestamped, sequential
├── seed.sql                    # Dev data (sample org, users, PRs)
└── functions/                  # Edge Functions (if needed later)
    └── .gitkeep
```

### Migration Conventions
- Files named `YYYYMMDDHHMMSS_description.sql`
- Each migration is idempotent where possible (`CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`)
- Destructive migrations (drops, renames) require explicit `-- DESTRUCTIVE` comment header
- Migration diffs validated in CI via `supabase db diff`
