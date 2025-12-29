from typing import List, Optional
import chainlit as cl
from app.agents import create_producer_agent, create_critic_agent
from app.schemas import CritiqueResult
from app.config import config
import datetime

class Orchestrator:
    def __init__(self, document_content: str, question: str, max_iterations: int | None = None):
        self.document_content = document_content
        self.question = question
        self.max_iterations = max_iterations or config.max_iterations
        
        self.producer = create_producer_agent()
        self.critic = create_critic_agent()

    async def run(self):
        context = f"Document Content:\n{self.document_content}\n\nQuestion: {self.question}"
        
        current_answer = ""
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Phase 2: Producer generates draft
            async with cl.Step(name=f"Producer (Iteration {iteration})") as step:
                step.input = context if iteration == 1 else f"{context}\n\nPrevious Answer:\n{current_answer}\n\nCritique Feedback:\n{str(feedback_dict)}"
                
                # If it's not the first iteration, we should append the feedback
                # Ideally we pass message history, but simple prompt concatenation works for now
                prompt = f"Context:\n{context}"
                if iteration > 1:
                     prompt += f"\n\nRefine the following answer based on the critique.\nPrevious Answer: {current_answer}\nCritique: {feedback_dict}"
                else:
                    prompt += "\n\nPlease generate the initial answer."

                result = await self.producer.run(prompt)
                current_answer = result.output
                step.output = current_answer

            # Phase 3: Critic evaluates
            async with cl.Step(name=f"Critic (Iteration {iteration})") as step:
                step.input = f"Source Document: {self.document_content}\n\nUser Question: {self.question}\n\nProposed Answer: {current_answer}"
                
                critic_prompt = f"""
                Evaluate the following answer against the source document and question.
                
                Document: {self.document_content}
                Question: {self.question}
                Answer: {current_answer}
                
                Iteration ID: {iteration}
                Current Time: {datetime.datetime.now().isoformat()}
                """
                
                result = await self.critic.run(critic_prompt)
                critique: CritiqueResult = result.output
                
                # Format critique for human-readable display
                status_emoji = "✅" if critique.global_status == "PASS" else "❌"
                status_badge = f"**{status_emoji} {critique.global_status}**"
                
                # Format scores with visual indicators
                def format_score(score: float) -> str:
                    percentage = int(score * 100)
                    if score >= 0.8:
                        return f"🟢 {percentage}%"
                    elif score >= 0.5:
                        return f"🟡 {percentage}%"
                    else:
                        return f"🔴 {percentage}%"
                
                scores_display = f"""
**Quantitative Scores:**
- Groundedness: {format_score(critique.quantitative_scores.groundedness)}
- Recall: {format_score(critique.quantitative_scores.recall)}
- Precision: {format_score(critique.quantitative_scores.precision)}
- Logical Consistency: {format_score(critique.quantitative_scores.logical_consistency)}
- Instruction Following: {format_score(critique.quantitative_scores.instruction_following)}

**Critic Confidence:** {int(critique.critic_confidence_score * 100)}%
"""
                
                # Format actionable feedback
                feedback_display = ""
                if critique.actionable_feedback:
                    feedback_display = "\n**Actionable Feedback:**\n"
                    for i, feedback in enumerate(critique.actionable_feedback, 1):
                        severity_emoji = {"LOW": "ℹ️", "MEDIUM": "⚠️", "HIGH": "🚨"}.get(feedback.severity, "")
                        feedback_display += f"\n{i}. **{feedback.dimension}** {severity_emoji} {feedback.severity}\n"
                        feedback_display += f"   - Issue: {feedback.issue_description}\n"
                        feedback_display += f"   - Fix: {feedback.actionable_fix}\n"
                        if feedback.reference_snippets:
                            feedback_display += f"   - References: {', '.join(f'`{s[:50]}...`' for s in feedback.reference_snippets[:2])}\n"
                
                step.output = f"{status_badge}\n\n{scores_display}{feedback_display}"
                
            feedback_dict = critique.model_dump()
            
            # Check termination
            if critique.global_status == "PASS":
                return current_answer
            
            # Prepare for next loop
            # Check exhaustion at the start of loop or here? 
            # If this was the last iteration (iteration == max), we break and return whatever we have or fail?
            # Spec says "Exhaustion" is a termination condition.
            
        return current_answer
