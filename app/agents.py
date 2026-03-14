import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.litellm import LiteLLMProvider
from dotenv import load_dotenv
from app.schemas import CritiqueResult
from app.config import config

load_dotenv()

# System Prompts
PRODUCER_SYSTEM_PROMPT = """
You are the Producer Agent, a lead synthesizer.
Your goal is to analyze the source document and generate a comprehensive answer to the user's question.
Prioritize depth and narrative coherence.
You must cite specific sections of the document to ensure grounding.
Provide the answer in markdown.
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

def _resolve_model(model_name: str) -> str | OpenAIChatModel:
    """
    Resolve the model to use based on configuration.
    
    If Azure configuration is present, forces OpenAIChatModel with LiteLLMProvider.
    Otherwise, returns the model name string for PydanticAI to infer the provider.
    """
    if config.azure_api_key and config.azure_api_base:
        return OpenAIChatModel(
            model_name,
            provider=LiteLLMProvider(
                api_base=config.azure_api_base,
                api_key=config.azure_api_key
            )
        )
    return model_name


def create_producer_agent(
    model_name: str | None = None,
    temperature: float | None = None,
    model_settings: dict | None = None
) -> Agent:
    """
    Create the Producer agent with customizable parameters.
    
    Args:
        model_name: LiteLLM model identifier (e.g., "azure/gpt-4o"). 
                   If None, uses config.producer_model.
        temperature: Sampling temperature for generation.
                    If None, uses config.producer_temperature.
        model_settings: Additional LiteLLM parameters (max_tokens, top_p, etc.)
    
    Returns:
        Configured Producer Agent instance.
    """
    producer_config = config.get_producer_config()
    final_model_name = model_name or producer_config.model_name
    model = _resolve_model(final_model_name)
    
    # Merge temperature into model_settings
    final_settings = model_settings or {}
    final_settings["temperature"] = temperature if temperature is not None else producer_config.temperature
    
    return Agent(
        model,
        system_prompt=PRODUCER_SYSTEM_PROMPT,
        output_type=str,
        model_settings=final_settings
    )


def create_critic_agent(
    model_name: str | None = None,
    temperature: float | None = None,
    model_settings: dict | None = None
) -> Agent:
    """
    Create the Critic agent with structured output for evaluation.
    
    Args:
        model_name: LiteLLM model identifier (e.g., "azure/gpt-4o-mini").
                   If None, uses config.critic_model.
        temperature: Sampling temperature for generation.
                    If None, uses config.critic_temperature.
        model_settings: Additional LiteLLM parameters (max_tokens, top_p, etc.)
    
    Returns:
        Configured Critic Agent instance with CritiqueResult output type.
    """
    critic_config = config.get_critic_config()
    final_model_name = model_name or critic_config.model_name
    model = _resolve_model(final_model_name)
    
    # Merge temperature into model_settings
    final_settings = model_settings or {}
    final_settings["temperature"] = temperature if temperature is not None else critic_config.temperature
    
    return Agent(
        model,
        system_prompt=CRITIC_SYSTEM_PROMPT,
        output_type=CritiqueResult,
        model_settings=final_settings
    )
