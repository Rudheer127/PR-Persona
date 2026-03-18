# ReviewSense AI — Implementation Rules & Coding Standards

> These rules apply to all future code written for ReviewSense AI. Code must be structured as if written by a senior engineer at a production company.

---

## 1. Separation of Concerns

### Layer Responsibilities

| Layer | Allowed Dependencies | Responsibility |
|-------|---------------------|---------------|
| **Transport** (`api/routes/`) | Schemas, Services (via DI) | HTTP request/response handling, input validation, auth checks |
| **Services** (`services/`) | Repositories, Clients, Schemas | Business logic, orchestration, scoring, verdict computation |
| **Repositories** (`repositories/`) | Models, Supabase client | Data access, CRUD operations, query building |
| **Clients** (`clients/`) | Schemas (DTOs) | External service communication (LLM, GitHub) |
| **Schemas** (`schemas/`) | None (leaf node) | Data transfer objects, validation, serialization |
| **Models** (`models/`) | None (leaf node) | Database table representations |

### Rules
- **No HTTP concerns in services** — services never import `Request`, `Response`, or HTTP status codes
- **No business logic in routes** — routes delegate to services immediately after validation
- **No direct DB access in services** — always go through a repository
- **Clients are swappable** — all external clients implement a protocol/interface; mock implementations exist for testing

---

## 2. Typed Interfaces

### Python
```python
# All external boundaries use Pydantic v2 models with strict mode
from pydantic import BaseModel, ConfigDict

class AnalysisRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    pr_url: str
    user_id: str
    org_id: str | None = None

# All internal service interfaces use Protocol
from typing import Protocol

class LLMClient(Protocol):
    async def complete(self, prompt: str, schema: type[BaseModel]) -> BaseModel: ...
```

### TypeScript
```typescript
// All API boundaries use Zod schemas with inferred types
import { z } from 'zod';

export const AnalysisResultSchema = z.object({
  id: z.string().uuid(),
  socialHealthScore: z.number().min(0).max(100),
  verdict: z.enum(['VETO', 'PAUSE', 'CLEAR']),
  // ...
});

export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
```

### Rules
- **No `any` in TypeScript** — use `unknown` + type narrowing where type is uncertain
- **No untyped dicts in Python** — use `TypedDict` or Pydantic models for all structured data
- **Validate at boundaries** — every API request and external response is validated through schemas

---

## 3. Logging

### Structure
```python
import structlog

logger = structlog.get_logger()

# Every log entry includes:
# - correlation_id (from request header or generated)
# - timestamp (ISO 8601)
# - level (DEBUG/INFO/WARNING/ERROR)
# - event (human-readable description)
# - context fields (user_id, pr_url, etc.)

logger.info(
    "analysis_started",
    correlation_id=ctx.correlation_id,
    pr_url=request.pr_url,
    user_id=request.user_id,
)
```

### Rules
| ✅ Do | ❌ Don't |
|-------|---------|
| Log event names as snake_case | Log full sentences as event names |
| Include correlation_id on every log | Log without request context |
| Log latency for external calls | Log request/response bodies |
| Log error type and message | Log stack traces in production (use ERROR level for traces) |
| Log analysis verdict + score | Log PR comment text or OAuth tokens |
| Use structured key=value pairs | Use string interpolation for log messages |

### Sensitive Data Blocklist
Never log: `access_token`, `refresh_token`, `api_key`, `private_key`, `password`, `authorization` header values, PR comment content (use comment_id references instead)

---

## 4. Error Handling

### Exception Hierarchy (Python)
```python
class ReviewSenseError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class ValidationError(ReviewSenseError):        # 400
class AuthenticationError(ReviewSenseError):     # 401
class AuthorizationError(ReviewSenseError):      # 403
class NotFoundError(ReviewSenseError):           # 404
class RateLimitError(ReviewSenseError):          # 429
class ExternalServiceError(ReviewSenseError):    # 502
class AnalysisError(ReviewSenseError):           # 500
```

### Rules
- **User-facing messages are actionable** — "Analysis failed. The PR may be too large (>2000 files). Try a smaller PR." not "Internal server error"
- **Internal details are hidden** — stack traces, SQL errors, and LLM raw responses never reach the client
- **Error codes are machine-parseable** — e.g., `RATE_LIMIT_EXCEEDED`, `GITHUB_FETCH_FAILED`, `LLM_TIMEOUT`
- **Errors are logged with full context** — the internal log captures everything the user error message omits
- **Retry guidance** — 429 responses include `Retry-After` header; transient errors include `retryable: true` in response

---

## 5. Testing Strategy

### Unit Tests
| Target | Coverage Goal | Approach |
|--------|-------------|----------|
| `verdict_calculator` | 100% branch coverage | Test all flag combinations → VETO/PAUSE/CLEAR |
| `social_health_scorer` | ≥90% | Test score computation with edge cases (empty comments, single reviewer) |
| `file_classifier` | ≥95% | Test all file category mappings |
| `diff_parser` | ≥95% | Test with various diff stat formats |
| Pydantic schemas | ≥90% | Test validation, serialization, edge cases |

### Integration Tests
| Target | Approach |
|--------|----------|
| GitHub client | Use recorded HTTP fixtures (VCR.py) against real API responses |
| Supabase repos | Use test Supabase project with seeded data; reset between test suites |
| Analysis orchestrator | Mock LLM client, real repos; verify end-to-end data flow |
| API routes | FastAPI `TestClient`; verify auth, rate limits, error responses |

### End-to-End Tests (Phase 2+)
| Target | Approach |
|--------|----------|
| Full analysis flow | Submit real PR URL → verify results stored → verify dashboard renders |
| Auth flow | GitHub OAuth → token storage → API access |
| Rate limiting | Exceed quota → verify 429 → verify recovery |

### Test Conventions
- Tests live in `tests/` mirroring `app/` structure
- Shared fixtures in `tests/conftest.py`
- Mock data in `tests/fixtures/`
- No sleeping in tests — use `asyncio` event control
- CI runs all unit tests on every PR; integration tests on merge to main

---

## 6. Observability

### Metrics to Track

| Metric | Type | Labels |
|--------|------|--------|
| `analysis_duration_seconds` | Histogram | `status`, `model` |
| `analysis_total` | Counter | `status` (success/failure), `verdict` |
| `llm_call_duration_seconds` | Histogram | `pipeline`, `model` |
| `llm_token_usage` | Counter | `pipeline`, `direction` (input/output) |
| `llm_error_total` | Counter | `error_type` |
| `github_api_calls_total` | Counter | `endpoint`, `status` |
| `rate_limit_hits_total` | Counter | `scope` (user/org/ip) |
| `verdict_distribution` | Counter | `verdict` (VETO/PAUSE/CLEAR) |
| `social_health_score` | Histogram | – |
| `judgement_score` | Histogram | – |

### Implementation
- Expose `/metrics` endpoint (Prometheus format) on the FastAPI service
- Use `prometheus-fastapi-instrumentator` for automatic HTTP metrics
- Custom metrics via `prometheus_client` library
- Dashboard via Grafana or equivalent (Phase 2+)

---

## 7. Configurability

### Per-Team Configurable Thresholds

| Parameter | Default | Stored In | Used By |
|-----------|---------|-----------|---------|
| Max PR size (lines) | 500 | `team_norms.max_pr_lines` | Social health scorer (engagement expectations) |
| Min comments per 100 LOC | 2 | `team_norms.min_comments_per_100loc` | Review depth calculation |
| Tone sensitivity | `medium` | `team_norms.tone_sensitivity` | LLM prompt modifier |
| Bias threshold | 0.80 | `team_norms.bias_threshold` | Flag trigger for author favoritism |
| Required reviewers | 1 | `team_norms.required_reviewers` | Engagement balance calculation |
| Daily analysis quota (user) | 50 | `team_norms.custom_config` | Rate limiter |
| Daily analysis quota (org) | 200 | `team_norms.custom_config` | Rate limiter |

### Rules
- **All thresholds have sensible defaults** — the system works out-of-the-box without configuration
- **Overrides are hierarchical** — org defaults < team overrides < explicit request params
- **Changes are audited** — `team_norms.updated_by` and `updated_at` track who changed what
- **Feature flags** — use a simple `feature_flags` JSONB column in `team_norms` for gradual rollouts
