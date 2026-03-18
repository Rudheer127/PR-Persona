-- Initial Schema Migration for ReviewSense AI

-- Users (extends Supabase Auth, which lives in auth.users)
CREATE TABLE public.profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id),
    github_username TEXT NOT NULL UNIQUE,
    display_name    TEXT,
    avatar_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Organizations (GitHub orgs)
CREATE TABLE public.organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_org_id   BIGINT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Org membership
CREATE TABLE public.org_members (
    org_id      UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id     UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role        TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    joined_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (org_id, user_id)
);

-- Repositories
CREATE TABLE public.repos (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    github_repo_id  BIGINT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    full_name       TEXT NOT NULL,       -- e.g., "org/repo"
    default_branch  TEXT DEFAULT 'main',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Pull Requests (cached metadata)
CREATE TABLE public.pull_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo_id         UUID REFERENCES public.repos(id) ON DELETE CASCADE,
    github_pr_id    BIGINT NOT NULL,
    number          INT NOT NULL,
    title           TEXT NOT NULL,
    author_username TEXT NOT NULL,
    state           TEXT NOT NULL,        -- open, closed, merged
    diff_stats      JSONB,               -- {additions, deletions, changed_files}
    created_at      TIMESTAMPTZ,
    merged_at       TIMESTAMPTZ,
    fetched_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (repo_id, number)
);

-- PR Analyses (one per analysis run)
CREATE TABLE public.pr_analyses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pr_id               UUID REFERENCES public.pull_requests(id) ON DELETE CASCADE,
    requested_by        UUID REFERENCES public.profiles(id),
    status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    social_health_score SMALLINT CHECK (social_health_score BETWEEN 0 AND 100),
    score_breakdown     JSONB,           -- {tone, clarity, psych_safety, engagement}
    persona_reactions   JSONB,           -- array of persona card objects
    reviewer_verdicts   JSONB,           -- array of {reviewer, verdict, flags, score}
    tone_rewrites       JSONB,           -- array of {original, rewritten, flag}
    error_message       TEXT,
    ai_model_used       TEXT,
    prompt_version      TEXT,
    latency_ms          INT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    completed_at        TIMESTAMPTZ
);

-- Reviewer Stats (rolling aggregates per reviewer per org)
CREATE TABLE public.reviewer_stats (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    reviewer_username   TEXT NOT NULL,
    total_reviews       INT DEFAULT 0,
    approval_rate       NUMERIC(5,4),    -- 0.0000 to 1.0000
    avg_comment_depth   NUMERIC(6,2),    -- avg comments per review
    rubber_stamp_rate   NUMERIC(5,4),    -- % of approvals with <N comments
    domain_coverage     JSONB,           -- {file_pattern: review_count}
    avg_social_score    NUMERIC(5,2),
    avg_judgement_score NUMERIC(5,2),
    verdict_history     JSONB,           -- {veto: N, pause: N, clear: N}
    last_updated        TIMESTAMPTZ DEFAULT now(),
    UNIQUE (org_id, reviewer_username)
);

-- Team Norms (per-org configuration)
CREATE TABLE public.team_norms (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    max_pr_lines        INT DEFAULT 500,
    min_comments_per_100loc INT DEFAULT 2,
    tone_sensitivity    TEXT DEFAULT 'medium'
                        CHECK (tone_sensitivity IN ('low', 'medium', 'high')),
    required_reviewers  INT DEFAULT 1,
    bias_threshold      NUMERIC(5,4) DEFAULT 0.8000,
    custom_config       JSONB DEFAULT '{}',
    updated_by          UUID REFERENCES public.profiles(id),
    updated_at          TIMESTAMPTZ DEFAULT now(),
    UNIQUE (org_id)
);

-- OAuth tokens (encrypted, for GitHub API access)
CREATE TABLE public.oauth_tokens (
    user_id         UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    provider        TEXT NOT NULL DEFAULT 'github',
    access_token    TEXT NOT NULL,       -- Should be encrypted at rest via Supabase vault
    refresh_token   TEXT,
    scopes          TEXT[],
    expires_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Profiles: users can read all profiles, update only their own
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY profiles_select ON public.profiles FOR SELECT USING (true);
CREATE POLICY profiles_update ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Org members: visible to members of the same org
ALTER TABLE public.org_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_members_select ON public.org_members FOR SELECT
    USING (user_id = auth.uid() OR org_id IN (
        SELECT org_id FROM public.org_members WHERE user_id = auth.uid()
    ));

-- PR analyses: visible to requester + org members
ALTER TABLE public.pr_analyses ENABLE ROW LEVEL SECURITY;
CREATE POLICY analyses_select ON public.pr_analyses FOR SELECT
    USING (requested_by = auth.uid() OR EXISTS (
        SELECT 1 FROM public.pull_requests pr
        JOIN public.repos r ON r.id = pr.repo_id
        JOIN public.org_members om ON om.org_id = r.org_id
        WHERE pr.id = pr_analyses.pr_id AND om.user_id = auth.uid()
    ));

-- Reviewer stats: visible to org members, individual detail only to self
ALTER TABLE public.reviewer_stats ENABLE ROW LEVEL SECURITY;
CREATE POLICY reviewer_stats_select ON public.reviewer_stats FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM public.org_members WHERE user_id = auth.uid()
    ));

-- Team norms: readable by org members, writable by owner/admin
ALTER TABLE public.team_norms ENABLE ROW LEVEL SECURITY;
CREATE POLICY norms_select ON public.team_norms FOR SELECT
    USING (org_id IN (
        SELECT org_id FROM public.org_members WHERE user_id = auth.uid()
    ));
CREATE POLICY norms_update ON public.team_norms FOR UPDATE
    USING (org_id IN (
        SELECT org_id FROM public.org_members
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    ));
