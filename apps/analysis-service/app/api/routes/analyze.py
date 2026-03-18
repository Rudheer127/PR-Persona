from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import structlog
import re

from app.integrations.github_client import github_client
from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import AnalysisResult
from app.api.deps import verify_api_key
from app.services.analysis_orchestrator import analysis_orchestrator

logger = structlog.get_logger()
router = APIRouter(prefix="/analyze", tags=["analysis"])

class AnalyzeRequest(BaseModel):
    pr_url: str
    user_id: str

def parse_github_url(url: str) -> tuple[str, str, int]:
    """Parse a GitHub PR URL into owner, repo, and pull number."""
    # e.g., https://github.com/Rudheer127/PR-Persona/pull/1
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        raise ValueError("Invalid GitHub PR URL")
    return match.group(1), match.group(2), int(match.group(3))

@router.post("", response_model=dict, dependencies=[Depends(verify_api_key)])
async def analyze_pr(req: AnalyzeRequest):
    try:
        # 1. Parse URL
        owner, repo, pr_number = parse_github_url(req.pr_url)
        logger.info("analysis_requested", owner=owner, repo=repo, pr=pr_number, user_id=req.user_id)
        
        # 2. Fetch from GitHub 
        raw_data = await github_client.fetch_pr_data(owner, repo, pr_number)
        
        # 3. Normalize to AnalyzablePR (mock implementation for scaffold)
        pr_metadata = AnalyzablePR(
            number=pr_number,
            title=raw_data["pr"].get("title", ""),
            author=raw_data["pr"]["user"]["login"],
            state=raw_data["pr"]["state"],
            url=req.pr_url,
            additions=raw_data["pr"].get("additions", 0),
            deletions=raw_data["pr"].get("deletions", 0),
            changed_files=raw_data["pr"].get("changed_files", 0),
            file_list=[f["filename"] for f in raw_data["files"]]
        )

        # 4. Trigger Analysis Orchestrator
        result = await analysis_orchestrator.run(pr_metadata)
        
        return {
            "status": "processing",
            "message": f"Analysis completed for PR #{pr_number}",
            "pr_metadata": pr_metadata.model_dump(),
            "analysis_result": result.model_dump()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("analysis_failed", error=str(e), pr_url=req.pr_url)
        raise HTTPException(status_code=500, detail="Internal analysis error")
