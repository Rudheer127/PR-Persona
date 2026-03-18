import structlog
import asyncio

from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import AnalysisResult
from app.services.persona_analyzer import persona_analyzer
from app.services.judgement_analyzer import judgement_analyzer
from app.services.social_health_scorer import social_health_scorer

logger = structlog.get_logger()

class AnalysisOrchestrator:
    async def run(self, pr: AnalyzablePR) -> AnalysisResult:
        logger.info("analysis_orchestration_started", pr_number=pr.number)
        
        # Run three pipelines concurrently
        persona_task = persona_analyzer.analyze(pr)
        judgement_task = judgement_analyzer.analyze(pr)
        social_task = social_health_scorer.score(pr)
        
        persona_reactions, reviewer_verdicts, (social_score, breakdown) = await asyncio.gather(
            persona_task, judgement_task, social_task
        )
        
        # Assemble Result
        result = AnalysisResult(
            social_health_score=social_score,
            score_breakdown=breakdown,
            persona_reactions=persona_reactions,
            reviewer_verdicts=reviewer_verdicts,
            tone_rewrites=[]
        )
        
        logger.info("analysis_orchestration_completed", pr_number=pr.number, score=social_score)
        return result

analysis_orchestrator = AnalysisOrchestrator()
