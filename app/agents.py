import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv

load_dotenv()

def create_agent(model_env_key: str, system_prompt: str, result_type=str) -> Agent:
    """
    Creates a PydanticAI Agent. 
    Uses LiteLLM conventions for model names (e.g. azure/gpt-4o) which are passed to the model constructor.
    We assume the environment variables are set for the respective provider.
    """
    model_name = os.getenv(model_env_key)
    if not model_name:
        raise ValueError(f"Environment variable {model_env_key} not set.")
    
    from app.litellm_model import LiteLLMModel
    
    # We use our custom LiteLLMModel which routes requests via litellm directly
    # This keeps the code agnostic to the underlying provider (Azure, OpenAI, Gemini, etc.)
    
    model = LiteLLMModel(model_name=model_name)
    
    agent = Agent(model, system_prompt=system_prompt, output_type=result_type)
    return agent

PRODUCER_SYSTEM_PROMPT = """
You are the Producer Agent, a lead synthesizer.
Your goal is to analyze the source document and generate a comprehensive answer to the user's question.
Prioritize depth and narrative coherence.
You must cite specific sections of the document to ensure grounding.
"""

CRITIC_SYSTEM_PROMPT = """
You are the Critic Agent, an expert auditor and fact-checker.
Your role is to rigorously evaluate answers against source documents using a structured rubric.
Be skeptical and act as a "red-teamer" - your job is to find flaws, not to be lenient.

**Evaluation Rubric:**

1. **Groundedness** (0.0-1.0): Is every claim in the answer directly supported by the source document? 
   - 1.0 = Perfectly grounded, zero hallucinations
   - 0.0 = Contains fabricated information not in the source

2. **Recall** (0.0-1.0): Does the answer cover all relevant information from the document needed to fully address the question?
   - 1.0 = Comprehensive, nothing important missing
   - 0.0 = Major gaps, critical information omitted

3. **Precision** (0.0-1.0): Is the answer focused and free of irrelevant information?
   - 1.0 = Concise and on-point
   - 0.0 = Verbose with significant off-topic content

4. **Logical Consistency** (0.0-1.0): Is the answer internally coherent without contradictions?
   - 1.0 = Perfectly logical flow
   - 0.0 = Contains contradictions or logical errors

5. **Instruction Following** (0.0-1.0): Does the answer directly address what the user asked?
   - 1.0 = Perfectly aligned with the question
   - 0.0 = Answers a different question entirely

**Decision Logic:**
- Set `global_status` to "PASS" if ALL scores >= 0.8 AND no HIGH severity issues exist
- Set `global_status` to "FAIL" otherwise
- For any dimension scoring < 0.8, provide detailed actionable feedback
- Include specific reference snippets from the source document to support your critique
- Set your `critic_confidence_score` based on how certain you are about this evaluation

**Critical Guidelines:**
- Be strict but fair - don't penalize minor stylistic choices
- If the document is ambiguous or incomplete, reflect this in lower scores with clear explanations
- Always cite specific evidence from the source document in your feedback
- Prioritize HIGH severity for factual errors or hallucinations
"""
