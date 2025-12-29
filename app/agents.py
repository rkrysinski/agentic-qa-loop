import os
from pydantic_ai import Agent
from dotenv import load_dotenv
from app.litellm_model import LiteLLMModel
from app.schemas import CritiqueResult

load_dotenv()

# System Prompts
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


def create_producer_agent(
    model_name: str | None = None,
    temperature: float = 1.0
) -> Agent:
    """
    Create the Producer agent with customizable parameters.
    
    Args:
        model_name: LiteLLM model identifier (e.g., "azure/gpt-4o"). 
                   If None, reads from PRODUCER_MODEL env var.
        temperature: Sampling temperature for generation.
    
    Returns:
        Configured Producer Agent instance.
    """
    if model_name is None:
        model_name = os.getenv("PRODUCER_MODEL")
        if not model_name:
            raise ValueError("PRODUCER_MODEL environment variable not set and no model_name provided.")
    
    model = LiteLLMModel(model_name=model_name, temperature=temperature)
    
    return Agent(
        model,
        system_prompt=PRODUCER_SYSTEM_PROMPT,
        output_type=str
    )


def create_critic_agent(
    model_name: str | None = None,
    temperature: float = 1.0
) -> Agent:
    """
    Create the Critic agent with structured output for evaluation.
    
    Args:
        model_name: LiteLLM model identifier (e.g., "azure/gpt-4o-mini").
                   If None, reads from CRITIC_MODEL env var.
        temperature: Sampling temperature for generation.
    
    Returns:
        Configured Critic Agent instance with CritiqueResult output type.
    """
    if model_name is None:
        model_name = os.getenv("CRITIC_MODEL")
        if not model_name:
            raise ValueError("CRITIC_MODEL environment variable not set and no model_name provided.")
    
    model = LiteLLMModel(model_name=model_name, temperature=temperature)
    
    return Agent(
        model,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        output_type=CritiqueResult
    )
