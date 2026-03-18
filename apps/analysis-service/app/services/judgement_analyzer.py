import json
import structlog
from app.schemas.pr import AnalyzablePR
from app.schemas.analysis import Verdict, Severity, Flag
from app.integrations.llm import llm_client

logger = structlog.get_logger()

class JudgementAnalyzer:
    async def analyze(self, pr: AnalyzablePR) -> list[dict]:
        logger.info("judgement_analysis_started", pr_number=pr.number)
        
        pr_context = f"""
        PR #{pr.number}: {pr.title}
        Author: {pr.author}
        Additions: {pr.additions}, Deletions: {pr.deletions}, Changed Files: {pr.changed_files}
        """

        prompt = f"""
        Analyze the pull request metadata below to identify risks regarding the reviewers' judgement and behavior.
        Look for signs of rubber stamping (approving massive PRs without comments), bias, or toxic nitpicking.
        
        PR Context:
        {pr_context}

        Output a JSON list of identified flags. If no flags are found, output an empty list [].
        Each flag must match this schema:
        {{
            "flag_type": str,
            "severity": "LOW", "MEDIUM", or "HIGH",
            "evidence": str (reason why this flag was raised),
            "suggestion": str (how to fix this problem)
        }}

        Return ONLY raw JSON. No markdown backticks.
        """

        mock_flags = []
        try:
            response_text = await llm_client.complete(prompt)
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            flags_data = json.loads(clean_text)
            mock_flags = [Flag(**item) for item in flags_data]
            logger.info("llm_judgement_flags_generated", count=len(mock_flags))
        except Exception as e:
            logger.error("judgement_llm_failed", error=str(e), fallback="deterministic")
            # Fallback to deterministic rules if LLM fails
            if pr.additions > 1000 and len(pr.reviews) == 0:
                mock_flags.append(Flag(
                    flag_type="rubber_stamp_risk",
                    severity=Severity.HIGH,
                    evidence="PR contains over 1000 additions but has no detailed review history.",
                    suggestion="Require at least one thorough review before merging."
                ))

        # Deterministic Verdict Logic (based on LLM output or fallback)
        final_verdict = Verdict.CLEAR
        for flag in mock_flags:
            if flag.severity == Severity.HIGH:
                final_verdict = Verdict.VETO
                break
            elif flag.severity == Severity.MEDIUM and final_verdict != Verdict.VETO:
                final_verdict = Verdict.PAUSE

        return [{
            "reviewer": pr.author, # Maps to overall PR for now
            "verdict": final_verdict,
            "flags": [f.model_dump() for f in mock_flags],
            "score": 50 if final_verdict == Verdict.VETO else 100
        }]

judgement_analyzer = JudgementAnalyzer()
