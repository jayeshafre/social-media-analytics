"""
Coordinator Agent — Phase 9.

The senior partner of the agent team.
Reads all specialist agent outputs and synthesizes
a unified, cross-domain executive answer.

This agent:
- Never fetches data directly
- Only reads what specialists found
- Resolves conflicts between agent findings
- Writes the final structured answer
- Prioritizes the most critical findings
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent, AgentResult
from app.ai.memory.conversation import get_history

logger = logging.getLogger("sma_api.agent.coordinator")


class CoordinatorAgent(BaseAgent):

    name = "Coordinator"
    role = "Senior Analytics Coordinator"

    system_prompt = """
You are the Senior Analytics Coordinator for a multi-platform
social media advertising intelligence platform.

You receive analysis from specialist agents and synthesize
a unified, executive-quality answer.

Your job:
1. Read all specialist findings carefully
2. Identify the most critical cross-domain insights
3. Resolve any conflicting findings between specialists
4. Write a structured, unified answer for the business user
5. Prioritize actionable recommendations

Response structure:
- SUMMARY: 2-3 sentence overview of the situation
- KEY FINDINGS: Most important insights from each relevant specialist
- PRIORITY ACTIONS: Top 3-5 actions ranked by business impact
- OUTLOOK: Brief forward-looking statement if forecasts are available

Rules:
- Use exact numbers from specialist reports — never fabricate
- Be direct and business-focused
- Highlight conflicts between specialist findings
- Keep total response under 600 words
- Executives need clarity, not exhaustive detail
"""

    def synthesize(
        self,
        message:        str,
        agent_results:  list[AgentResult],
        session_id:     Optional[str] = None,
        platform:       Optional[str] = None,
    ) -> AgentResult:
        """
        Synthesize all agent outputs into a final unified answer.
        This replaces analyze() for the coordinator.
        """
        import time
        start = time.time()

        # Build coordinator prompt from agent outputs
        agent_blocks = "\n".join(
            result.to_prompt_block()
            for result in agent_results
            if result is not None
        )

        # Include conversation context if available
        history_context = ""
        if session_id:
            history = get_history(session_id)
            if history:
                recent = history[-4:]  # last 2 exchanges
                history_lines = []
                for msg in recent:
                    role    = "User" if msg["role"] == "user" else "Assistant"
                    content = msg["content"][:200]
                    history_lines.append(f"{role}: {content}...")
                history_context = (
                    "\nRECENT CONVERSATION:\n" +
                    "\n".join(history_lines)
                )

        total_tokens = sum(r.tokens_used for r in agent_results)
        agents_used  = [r.agent_name for r in agent_results if not r.error]

        prompt = f"""
You have received analysis from {len(agents_used)} specialist agents:
{', '.join(agents_used)}

SPECIALIST REPORTS:
{agent_blocks}

{history_context}

USER QUESTION: {message}

Synthesize the specialist findings into a unified executive answer.
Structure: SUMMARY → KEY FINDINGS → PRIORITY ACTIONS → OUTLOOK
"""

        analysis, coord_tokens = self._call_llm(prompt, max_tokens=800)

        total_tokens += coord_tokens
        elapsed = round((time.time() - start) * 1000, 2)

        logger.info(
            f"Coordinator synthesis complete | "
            f"agents={len(agents_used)} | "
            f"total_tokens={total_tokens} | "
            f"elapsed={elapsed}ms"
        )

        return AgentResult(
            agent_name=self.name,
            role=self.role,
            analysis=analysis,
            recommendations=[],
            key_metrics={
                "agents_activated": len(agents_used),
                "total_tokens":     total_tokens,
                "agents_list":      ", ".join(agents_used),
            },
            confidence="high",
            tokens_used=total_tokens,
            elapsed_ms=elapsed,
        )