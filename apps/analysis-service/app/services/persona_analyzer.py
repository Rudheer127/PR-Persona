import json
import structlog
from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import PersonaReaction, Severity
from app.integrations.llm import llm_client

logger = structlog.get_logger()

class PersonaAnalyzer:
    async def analyze(self, pr: AnalyzablePR) -> list[dict]:
        logger.info("persona_analysis_started", pr_number=pr.number)
        
        pr_context = f"""
        PR #{pr.number}: {pr.title}
        Author: {pr.author}
        Additions: {pr.additions}, Deletions: {pr.deletions}, Changed Files: {pr.changed_files}
        """

        prompt = f"""
        You are simulating two personas reviewing a GitHub Pull Request:
        1. "Junior Dev": Needs clear instructions, easily confused by complex magic, prioritizes safety.
        2. "Burned Senior": Pragmatic, hates tech debt, looks for maintainability traps.

        Here is the PR Context:
        {pr_context}

        Provide your reaction as a JSON list containing exactly two objects matching this schema:
        {{
            "persona_name": str,
            "emotional_reaction": str (a single emoji),
            "clarity_score": int (0 to 100),
            "friction_risk": "LOW", "MEDIUM", or "HIGH",
            "narrative": str (a one sentence reaction in character)
        }}

        Return ONLY raw JSON. No markdown backticks.
        """

        try:
            # We call the OpenAI-compatible Hugging Face router
            response_text = await llm_client.complete(prompt)
            
            # Clean possible markdown block
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            reactions_data = json.loads(clean_text)
            
            # Validate via Pydantic using our schema
            valid_reactions = [PersonaReaction(**item).model_dump() for item in reactions_data]
            return valid_reactions
            
        except json.JSONDecodeError as e:
            logger.error("persona_parsing_failed", error=str(e), response=response_text)
            return []
        except Exception as e:
            logger.error("persona_generation_failed", error=str(e))
            return []

persona_analyzer = PersonaAnalyzer()
