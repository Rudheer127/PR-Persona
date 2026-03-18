import httpx
import structlog
from app.core.config import settings
from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import AnalysisResult

logger = structlog.get_logger()

class SupabaseRepoError(Exception):
    pass

class SupabaseRepository:
    def __init__(self):
        # We use the Supabase REST API (PostgREST)
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def save_analysis(self, pr: AnalyzablePR, result: AnalysisResult, user_id: str) -> dict:
        """Saves or updates the PR and inserts the Analysis run."""
        try:
            async with httpx.AsyncClient(headers=self.headers, base_url=self.base_url) as client:
                
                # 1. Upsert dummy Org and Repo to satisfy foreign keys for scaffold
                # In production, we assume repos exist via GitHub App installation sync
                org_res = await client.post(
                    "/organizations?on_conflict=github_org_id",
                    json={"github_org_id": 1, "name": "Scaffold Org", "slug": "scaffold-org"}
                )
                
                repo_res = await client.post(
                    "/repos?on_conflict=github_repo_id",
                    json={
                        "github_repo_id": 1, 
                        "org_id": org_res.json()[0]["id"] if org_res.status_code == 201 else None, 
                        "name": "scaffold-repo", 
                        "full_name": "scaffold/repo"
                    }
                )
                repo_id = repo_res.json()[0]["id"] if repo_res.status_code in [200, 201] else None

                # 2. Upsert PR
                pr_payload = {
                    "repo_id": repo_id,
                    "github_pr_id": pr.number, # Mock PR ID
                    "number": pr.number,
                    "title": pr.title,
                    "author_username": pr.author,
                    "state": pr.state,
                    "diff_stats": {
                        "additions": pr.additions,
                        "deletions": pr.deletions,
                        "changed_files": pr.changed_files
                    }
                }
                
                pr_res = await client.post(
                    "/pull_requests?on_conflict=repo_id,number",
                    json=pr_payload
                )
                pr_res.raise_for_status()
                db_pr_id = pr_res.json()[0]["id"]

                # 3. Insert Analysis
                analysis_payload = {
                    "pr_id": db_pr_id,
                    "requested_by": user_id,
                    "status": "completed",
                    "social_health_score": result.social_health_score,
                    "score_breakdown": result.score_breakdown.model_dump(),
                    "persona_reactions": [p.model_dump() for p in result.persona_reactions],
                    "reviewer_verdicts": result.reviewer_verdicts,
                    "tone_rewrites": result.tone_rewrites,
                    "ai_model_used": settings.hf_model_name
                }
                
                an_res = await client.post("/pr_analyses", json=analysis_payload)
                an_res.raise_for_status()
                
                return an_res.json()[0]

        except httpx.HTTPStatusError as e:
            logger.error("supabase_db_error", status=e.response.status_code, body=e.response.text)
            raise SupabaseRepoError(f"Database error: {e.response.status_code}") from e
        except Exception as e:
            logger.error("supabase_client_error", error=str(e))
            raise SupabaseRepoError("Failed to communicate with Supabase") from e

supabase_repo = SupabaseRepository()
