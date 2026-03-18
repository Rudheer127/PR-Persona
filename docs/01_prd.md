# ReviewSense AI — Product Requirements Document (MVP)

## 1. Overview

**ReviewSense AI** is a GitHub-integrated assistant that evaluates pull request reviews through the lens of **social dynamics, cultural health, and reviewer judgement quality** — not just code correctness. Its signature capability: it **judges the reviewer**, issuing a verdict (VETO / PAUSE / CLEAR) on whether that person is truly qualified to approve a given PR right now, based on bias patterns, domain coverage, confidence calibration, and historical blind spots.

### Tagline
> "The AI that judges whether *you* are qualified to review this PR."

---

## 2. Problem Statement

Code review tools today focus almost exclusively on static analysis, linting, and superficial "AI suggestions." They miss the **human layer** — the layer where:

- A senior rubber-stamps PRs from a favored author without reading diffs.
- A reviewer lacks domain context for the files changed but approves anyway.
- Tone and framing in review comments create psychological friction, discouraging contribution.
- Teams have no visibility into whether their review culture is healthy or deteriorating.

**ReviewSense AI** surfaces these invisible risks before they compound into attrition, bugs, and cultural decay.

---

## 3. Goals & Non-Goals

### Goals (MVP)
| # | Goal |
|---|------|
| G1 | Analyze a single PR's review comments for social/cultural tone and friction risk |
| G2 | Simulate how different personas (Team Lead, Junior Dev, "Burned" Senior) perceive the review |
| G3 | Issue a VETO / PAUSE / CLEAR verdict on the reviewer's qualification for this specific PR |
| G4 | Compute a **Social Health Score** (tone/culture) and a **Reviewer Judgement Score** (bias/coverage) |
| G5 | Provide actionable, non-shaming explanations for every flag |
| G6 | Store analysis history per reviewer (aggregated, anonymizable) for trend detection |
| G7 | Offer a lightweight team-level health dashboard |

### Non-Goals (MVP)
- Deep org-level BI dashboards or multi-team rollups
- Multi-VCS support (GitLab, Bitbucket)
- Custom LLM fine-tuning or self-hosted model serving
- Real-time in-GitHub comment composer or bot auto-reply
- Heavy multi-org administration or SSO beyond GitHub OAuth
- Performance profiling or runtime analysis of the code itself

---

## 4. Users & Personas

| Persona | Role | Primary Need |
|---------|------|-------------|
| **PR Author** | IC engineer | *"How will this review land on my team?"* — understand tone, friction risks, and get suggested rewrites before comments go live |
| **Senior Reviewer** | Staff / Senior engineer | *"Am I actually qualified to approve this PR right now?"* — see blind spots, bias tendencies, and coverage gaps for the specific changeset |
| **Team Lead / EM** | Engineering manager | *"Where is our review culture deteriorating?"* — spot trends (rubber-stamping spikes, lone-reviewer bottlenecks, rising friction scores) without creating surveillance anxiety |
| **People Ops** *(Phase 2+)* | HR / culture lead | Access anonymized, aggregate review-health data for org-health initiatives |

---

## 5. Scope

### 5.1 In Scope (MVP)

1. **PR Ingestion** — paste a GitHub PR URL *or* select from connected repos via GitHub App
2. **Persona Reaction Cards** — simulated responses from ≥3 configurable personas showing how each would perceive the review comments (emotional reaction, clarity rating, friction risk)
3. **Reviewer Judgement Verdict** — per-reviewer VETO / PAUSE / CLEAR with structured explanation
4. **Social Health Score** (0–100) — composite of tone, clarity, psychological safety, constructiveness
5. **Reviewer Judgement Score** (0–100) — composite of bias indicators, domain coverage, confidence calibration
6. **Bias Detection Signals**:
   - Always-approve pattern for certain authors
   - Rubber-stamping large PRs (low comment density vs diff size)
   - Ignoring high-risk files (security, infra, migrations)
   - Over-confidence: high approval rate + low domain match
7. **Basic Norms Config** — per-team thresholds (max PR size, expected review depth, tone expectations)
8. **Analysis History** — stored per PR and per reviewer for trend views
9. **Lightweight Team Health View** — aggregated scores over time, top-risk PRs, reviewer workload balance
10. **Tone Rewrite Suggestions** — rephrase flagged comments to reduce friction

### 5.2 Out of Scope (MVP)
- Org-wide analytics beyond a single team
- Slack / Teams / email integrations
- Custom persona creation UI (hardcoded/config-only for MVP)
- Real-time GitHub webhook-driven analysis (user-initiated only)
- Code correctness analysis (linting, security scanning, etc.)

---

## 6. User Stories

### PR Author
| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| UA-1 | As a PR author, I can paste a PR URL and see persona reactions within 30 seconds | Persona cards render with emotional reaction, clarity rating, friction score |
| UA-2 | As a PR author, I can view suggested rewrites for flagged review comments | Each flagged comment shows original + rewritten version side-by-side |
| UA-3 | As a PR author, I can re-run analysis after the reviewer updates comments | Delta view showing score changes between runs |
| UA-4 | As a PR author, I can copy a rewritten comment to my clipboard | One-click copy button on each suggestion |

### Senior Reviewer
| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| UR-1 | As a reviewer, I can check my qualification verdict before approving a PR | VETO/PAUSE/CLEAR badge with structured rationale |
| UR-2 | As a reviewer, I can see which files in this PR fall outside my demonstrated domain expertise | File-level coverage heatmap (known / partial / unknown) |
| UR-3 | As a reviewer, I can see my historical bias patterns (e.g., rubber-stamp rate) | Trend chart of approval rate, comment depth, and domain match over last N PRs |
| UR-4 | As a reviewer, I can get tone-improvement suggestions for my own comments | Flagged comments with friction risk and rewrite suggestions |

### Team Lead / EM
| ID | Story | Acceptance Criteria |
|----|-------|-------------------|
| UL-1 | As a team lead, I can view a team health dashboard without seeing individual shaming scores | Aggregate view: avg Social Health, avg Judgement Score, trend lines, high-risk PR count |
| UL-2 | As a team lead, I can identify PRs that were approved despite high risk signals | Filterable list of PRs with VETO/PAUSE verdicts that were still merged |
| UL-3 | As a team lead, I can configure team norms (PR size limits, expected review depth) | Settings page with per-team threshold controls |
| UL-4 | As a team lead, I can see reviewer workload distribution | Bar chart of reviews per person over configurable time window |

---

## 7. Functional Requirements

### FR-1: PR Ingestion & Normalization
- Accept GitHub PR URL or repo+PR number; fetch via GitHub API (REST v3 / GraphQL v4)
- Extract: diff metadata (files changed, additions, deletions), review comments (inline + top-level), review state (approved/changes_requested/commented), author, reviewers, timestamps
- Normalize into an internal `AnalyzablePR` schema before passing to AI

### FR-2: Persona Reaction Simulation
- Run AI analysis against ≥3 built-in personas:
  - **Team Lead** — focuses on process compliance, risk, team dynamics
  - **Junior Developer** — focuses on clarity, approachability, learning signals
  - **"Burned" Senior** — focuses on passive aggression, dismissiveness, hidden assumptions
- Each persona produces: emotional_reaction (enum), clarity_score (0–10), friction_risk (low/medium/high/critical), narrative (2–3 sentences)

### FR-3: Reviewer Judgement Verdict
- Per reviewer on the PR, compute VETO / PAUSE / CLEAR:
  - **VETO** — strong signal that this reviewer should not be the sole approver (≥2 high-severity flags)
  - **PAUSE** — moderate concern; recommend a second opinion (1 high or ≥2 medium flags)
  - **CLEAR** — no significant bias/coverage/confidence flags detected
- Flags taxonomy:
  - `BIAS_AUTHOR_FAVORITISM` — disproportionately high approval rate for this PR author
  - `BIAS_RUBBER_STAMP` — approved with minimal engagement relative to diff size
  - `BLIND_SPOT_DOMAIN` — changed files fall outside reviewer's demonstrated expertise
  - `BLIND_SPOT_RISKY_FILES` — reviewer did not comment on security/infra/migration files
  - `CONFIDENCE_GAP` — historically high approval rate but low accuracy (reverts, post-merge bugs)
  - `TONE_FRICTION` — reviewer's comments scored high on friction risk
- Each flag includes: severity (low/medium/high), evidence summary, suggestion

### FR-4: Social Health Score
- Composite 0–100 score aggregating:
  - Tone analysis (politeness, constructiveness, empathy) — 40%
  - Clarity (specificity, actionability of comments) — 25%
  - Psychological safety signals (question framing, blame-free language) — 20%
  - Engagement balance (comment distribution across reviewers) — 15%
- Displayed with breakdown and per-dimension sub-scores

### FR-5: Reviewer Judgement Score
- Composite 0–100 score aggregating:
  - Domain coverage for this PR's changeset — 30%
  - Historical bias indicators — 25%
  - Review depth vs PR complexity — 25%
  - Confidence calibration (approval rate vs post-merge issue rate) — 20%

### FR-6: History & Trends
- Store each analysis run with timestamp, scores, verdict, flags
- Per-reviewer aggregate stats updated on each analysis
- Team-level aggregates computed from reviewer stats

### FR-7: Team Norms Configuration
- Configurable per team: max PR size (lines), min review comments per 100 LOC changed, tone sensitivity level, required reviewer count
- Norms feed into score calculations as weighted modifiers

### FR-8: Tone Rewrite Suggestions
- For comments flagged with friction risk ≥ medium, generate 1–2 alternative phrasings
- Preserve the reviewer's intent while reducing friction

---

## 8. Non-Functional Requirements

### NFR-1: Privacy & Data Minimization
- Store only fields necessary for analysis (no full file contents, no credentials)
- All PR data deletable on user request (soft-delete + hard purge after retention window)
- No training on customer data without explicit, documented consent

### NFR-2: Security
- GitHub OAuth with minimum necessary scopes (`repo:read`, `pull_request:read`)
- Supabase Row-Level Security on all user-scoped tables
- All secrets via environment variables; no hardcoded credentials anywhere
- HTTPS everywhere; API keys rotatable without downtime

### NFR-3: Performance
- PR analysis completes within 30 seconds for PRs ≤500 changed lines
- Dashboard loads within 2 seconds for teams ≤20 members
- AI service supports ≥10 concurrent analyses per instance

### NFR-4: Reliability
- AI service gracefully degrades if LLM provider is unavailable (cached partial results, clear error messaging)
- Idempotent analysis — re-running on same PR version produces consistent scores (±5%)

### NFR-5: Psychological Safety Ethics
- All verdicts presented as **guidance, not absolute judgement**
- No shaming language in any system output
- Aggregate/anonymous views for leadership; individual views only visible to the individual themselves
- Opt-in usage — no forced enrollment; reviewers can see their own data, team leads see only aggregates
- Explicit disclaimer: "This is AI-assisted guidance. Use professional judgement."

---

## 9. Assumptions

1. Users authenticate via GitHub OAuth; we do not support other identity providers in MVP.
2. LLM provider is OpenAI (GPT-4-class model) accessed via API; provider is swappable via adapter pattern.
3. A single "team" maps to a GitHub organization or a subset of repos within one org.
4. MVP supports English-language PR comments only.
5. Reviewer history is bootstrapped from GitHub API data on first connection, not imported from external systems.
6. Rate limits for AI analysis default to 50 analyses/user/day and 200/org/day, configurable.
