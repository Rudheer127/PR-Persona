import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class GitHubClientError(Exception):
    pass

class GitHubClient:
    """External client for fetching PR metadata from GitHub."""
    def __init__(self):
        # We will use the GitHub App flow or standard PAT if configured
        # For simplicity in Phase 0.5, we assume public repos or basic auth
        # In a real setup, we would generate a JWT for the GitHub App
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ReviewSense-AI",
        }

    async def fetch_pr_data(self, owner: str, repo: str, pull_number: int) -> dict:
        """Fetch raw PR data, reviews, and comments."""
        try:
            async with httpx.AsyncClient(headers=self.headers, base_url=self.base_url) as client:
                # 1. Fetch main PR
                pr_res = await client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")
                pr_res.raise_for_status()
                pr_data = pr_res.json()

                # 2. Fetch comments (review comments + issue comments)
                # Omitted for brevity: we would paginate and merge these
                
                # 3. Fetch reviews
                reviews_res = await client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews")
                reviews_res.raise_for_status()
                reviews_data = reviews_res.json()

                # 4. Fetch files
                files_res = await client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/files")
                files_res.raise_for_status()
                files_data = files_res.json()

                return {
                    "pr": pr_data,
                    "reviews": reviews_data,
                    "files": files_data,
                }
        except httpx.HTTPStatusError as e:
            logger.error("github_api_error", status_code=e.response.status_code, url=str(e.request.url))
            raise GitHubClientError(f"GitHub API returned {e.response.status_code}") from e
        except Exception as e:
            logger.error("github_client_error", error=str(e))
            raise GitHubClientError("Failed to communicate with GitHub API") from e

github_client = GitHubClient()
