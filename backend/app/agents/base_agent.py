"""
Base Agent — Phase 9.

Defines the interface every specialist agent must implement.
Enforces consistent input/output contract across all agents.

Design principles:
- Each agent is fully self-contained
- Each agent has its own system prompt and data scope
- Each agent returns a structured AgentResult
- Agents never call each other — only the coordinator reads them
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy.orm import Session
from app.ai.groq_client import groq_client
from app.core.config import settings

logger = logging.getLogger("sma_api.base_agent")


@dataclass
class AgentResult:
    """
    Structured output from any agent.
    The coordinator reads these to build the final answer.
    """
    agent_name:   str
    role:         str
    analysis:     str           # The agent's core findings
    recommendations: list[str]  # Specific action items
    key_metrics:  dict          # Important numbers found
    confidence:   str           # high | medium | low
    tokens_used:  int           # LLM tokens consumed
    elapsed_ms:   float         # Time taken
    error:        Optional[str] = None  # Error message if failed

    def to_prompt_block(self) -> str:
        """
        Format agent output for coordinator injection.
        Each agent's findings become a structured block.
        """
        if self.error:
            return f"[{self.agent_name}]: Analysis failed — {self.error}"

        rec_text = "\n".join(
            f"  - {r}" for r in self.recommendations
        ) if self.recommendations else "  - No specific recommendations"

        metrics_text = "\n".join(
            f"  {k}: {v}" for k, v in self.key_metrics.items()
        ) if self.key_metrics else "  No key metrics extracted"

        return f"""
═══ {self.agent_name.upper()} ({self.role}) ═══
Analysis:
{self.analysis}

Key Metrics Found:
{metrics_text}

Recommendations:
{rec_text}

Confidence: {self.confidence}
"""


class BaseAgent:
    """
    Abstract base class for all specialist agents.
    Subclasses must implement: name, role, system_prompt, analyze()
    """

    name:          str = "BaseAgent"
    role:          str = "Generic Analyst"
    system_prompt: str = "You are a marketing analytics specialist."

    def __init__(self):
        self.logger = logging.getLogger(f"sma_api.agent.{self.name}")

    def _call_llm(
        self,
        user_prompt: str,
        max_tokens:  int = 600,
    ) -> tuple[str, int]:
        """
        Make an LLM call with this agent's system prompt.
        Returns (response_text, tokens_used).
        """
        try:
            completion = groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.2,   # Low — agents must be analytical, not creative
                max_tokens=max_tokens,
            )
            text   = completion.choices[0].message.content
            tokens = completion.usage.total_tokens
            return text, tokens

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    def analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:
        """
        Main analysis method — must be implemented by each agent.
        """
        raise NotImplementedError(
            f"{self.name} must implement analyze()"
        )

    def _safe_analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:
        """
        Wraps analyze() with timing and error handling.
        Called by the router — never call analyze() directly.
        """
        start = time.time()
        try:
            result = self.analyze(
                message=message,
                db=db,
                platform=platform,
                time_period=time_period,
            )
            result.elapsed_ms = round((time.time() - start) * 1000, 2)
            self.logger.info(
                f"{self.name} complete | "
                f"tokens={result.tokens_used} | "
                f"elapsed={result.elapsed_ms}ms"
            )
            return result

        except Exception as e:
            self.logger.error(f"{self.name} failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                role=self.role,
                analysis="Analysis failed due to an internal error.",
                recommendations=[],
                key_metrics={},
                confidence="low",
                tokens_used=0,
                elapsed_ms=round((time.time() - start) * 1000, 2),
                error=str(e),
            )