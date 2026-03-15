from datetime import datetime
import chainlit as cl
from app.agents import create_producer_agent, create_critic_agent
from app.schemas import CritiqueResult
from app.config import config

_SEVERITY_EMOJI = {"LOW": "ℹ️", "MEDIUM": "⚠️", "HIGH": "🚨"}


class Orchestrator:
    def __init__(self, document_content: str, question: str, max_iterations: int | None = None):
        self.document_content = document_content
        self.question = question
        self.max_iterations = int(max_iterations or config.max_iterations)
        self.producer = create_producer_agent()
        self.critic = create_critic_agent()

    @staticmethod
    def _format_score(score: float) -> str:
        percentage = int(score * 100)
        if score >= 0.8:
            return f"🟢 {percentage}%"
        elif score >= 0.5:
            return f"🟡 {percentage}%"
        else:
            return f"🔴 {percentage}%"

    def _format_critique_output(self, critique: CritiqueResult) -> str:
        status_emoji = "✅" if critique.global_status == "PASS" else "❌"
        status_badge = f"**{status_emoji} {critique.global_status}**"

        scores = critique.quantitative_scores
        scores_display = (
            f"\n**Quantitative Scores:**\n"
            f"- Groundedness: {self._format_score(scores.groundedness)}\n"
            f"- Recall: {self._format_score(scores.recall)}\n"
            f"- Precision: {self._format_score(scores.precision)}\n"
            f"- Logical Consistency: {self._format_score(scores.logical_consistency)}\n"
            f"- Instruction Following: {self._format_score(scores.instruction_following)}\n\n"
            f"**Critic Confidence:** {int(critique.critic_confidence_score * 100)}%\n"
        )

        feedback_parts = []
        if critique.actionable_feedback:
            feedback_parts.append("\n**Actionable Feedback:**\n")
            for i, feedback in enumerate(critique.actionable_feedback, 1):
                severity_emoji = _SEVERITY_EMOJI.get(feedback.severity, "")
                feedback_parts.append(f"\n{i}. **{feedback.dimension}** {severity_emoji} {feedback.severity}\n")
                feedback_parts.append(f"   - Issue: {feedback.issue_description}\n")
                feedback_parts.append(f"   - Fix: {feedback.actionable_fix}\n")
                if feedback.reference_snippets:
                    refs = ", ".join(f"`{s[:50]}...`" for s in feedback.reference_snippets[:2])
                    feedback_parts.append(f"   - References: {refs}\n")

        return f"{status_badge}\n\n{scores_display}{''.join(feedback_parts)}"

    async def run(self) -> str:
        context = f"Document Content:\n{self.document_content}\n\nQuestion: {self.question}"
        current_answer = ""
        feedback_dict: dict | None = None

        for iteration in range(1, self.max_iterations + 1):
            # Producer generates answer
            async with cl.Step(name=f"Producer (Iteration {iteration})") as step:
                if iteration == 1:
                    step.input = context
                    prompt = f"Context:\n{context}\n\nPlease generate the initial answer."
                else:
                    step.input = f"{context}\n\nPrevious Answer:\n{current_answer}\n\nCritique Feedback:\n{feedback_dict}"
                    prompt = f"Context:\n{context}\n\nRefine the following answer based on the critique.\nPrevious Answer: {current_answer}\nCritique: {feedback_dict}"

                result = await self.producer.run(prompt)
                current_answer = result.output
                step.output = current_answer

            # Critic evaluates the answer
            async with cl.Step(name=f"Critic (Iteration {iteration})") as step:
                step.input = (
                    f"Source Document: {self.document_content}\n\n"
                    f"User Question: {self.question}\n\n"
                    f"Proposed Answer: {current_answer}"
                )
                critic_prompt = (
                    f"Evaluate the following answer against the source document and question.\n\n"
                    f"Document: {self.document_content}\n"
                    f"Question: {self.question}\n"
                    f"Answer: {current_answer}\n\n"
                    f"Iteration ID: {iteration}\n"
                    f"Current Time: {datetime.now().isoformat()}"
                )

                result = await self.critic.run(critic_prompt)
                critique: CritiqueResult = result.output
                step.output = self._format_critique_output(critique)

            feedback_dict = critique.model_dump()

            if critique.global_status == "PASS":
                return current_answer

        return current_answer
