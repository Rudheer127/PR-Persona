import structlog
from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import AnalysisResult, ScoreBreakdown

logger = structlog.get_logger()

class PersonaAnalyzer:
    async def analyze(self, pr: AnalyzablePR) -> list:
        # TODO: Implement LLM persona prompt calls
        logger.info("persona_analysis_started", pr_number=pr.number)
        return []

persona_analyzer = PersonaAnalyzer()
