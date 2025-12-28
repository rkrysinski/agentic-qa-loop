from typing import List, Optional
import chainlit as cl
from app.agents import create_agent, PRODUCER_SYSTEM_PROMPT, CRITIC_SYSTEM_PROMPT
from app.schemas import CritiqueResult
import datetime

class Orchestrator:
    def __init__(self, document_content: str, question: str):
        self.document_content = document_content
        self.question = question
        self.max_iterations = 3
        
        self.producer = create_agent("PRODUCER_MODEL", PRODUCER_SYSTEM_PROMPT)
        self.critic = create_agent("CRITIC_MODEL", CRITIC_SYSTEM_PROMPT, result_type=CritiqueResult)

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
                current_answer = result.data
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
                critique: CritiqueResult = result.data
                step.output = critique.model_dump_json(indent=2)
                
            feedback_dict = critique.model_dump()
            
            # Check termination
            if critique.global_status == "PASS":
                return current_answer
            
            # Prepare for next loop
            # Check exhaustion at the start of loop or here? 
            # If this was the last iteration (iteration == max), we break and return whatever we have or fail?
            # Spec says "Exhaustion" is a termination condition.
            
        return current_answer
