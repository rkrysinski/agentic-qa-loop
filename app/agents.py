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
You are the Critic Agent, an auditor and fact-checker.
Your goal is to evaluate the provided answer against the source document using the Critique Rubric.
You must be skeptical and act as a "red-teamer".
Provide structured feedback.
"""
