"""
Configuration management for the Agentic Q&A Loop application.

This module provides a centralized, type-safe configuration system using Pydantic.
All configuration values are loaded from environment variables with sensible defaults.
"""

import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    model_name: str = Field(..., description="LiteLLM model identifier (e.g., 'azure/gpt-4o')")
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="Sampling temperature")


class OrchestratorConfig(BaseModel):
    """Configuration for the orchestration loop."""
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum number of Producer-Critic iterations")
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum score threshold for PASS status")


class AppConfig(BaseSettings):
    """
    Main application configuration.
    
    All settings are loaded from environment variables with the following precedence:
    1. Environment variables
    2. .env file
    3. Default values defined here
    """
    
    # Producer Agent Configuration
    producer_model: str = Field(
        default="azure/gpt-5-mini",
        alias="PRODUCER_MODEL",
        description="Model for the Producer agent"
    )
    producer_temperature: float = Field(
        default=1.0,
        alias="PRODUCER_TEMPERATURE",
        description="Temperature for Producer agent"
    )
    
    # Critic Agent Configuration
    critic_model: str = Field(
        default="azure/gpt-4o",
        alias="CRITIC_MODEL",
        description="Model for the Critic agent"
    )
    critic_temperature: float = Field(
        default=0.4,
        alias="CRITIC_TEMPERATURE",
        description="Temperature for Critic agent"
    )
    
    # Orchestrator Configuration
    max_iterations: int = Field(
        default=3,
        alias="MAX_ITERATIONS",
        description="Maximum number of Producer-Critic iterations"
    )
    pass_threshold: float = Field(
        default=0.8,
        alias="PASS_THRESHOLD",
        description="Minimum score threshold for PASS status"
    )
    
    # Azure Configuration (optional, for reference)
    azure_api_key: str | None = Field(
        default=None,
        alias="AZURE_API_KEY",
        description="Azure OpenAI API key"
    )
    azure_api_base: str | None = Field(
        default=None,
        alias="AZURE_API_BASE",
        description="Azure OpenAI API base URL"
    )
    azure_api_version: str | None = Field(
        default=None,
        alias="AZURE_API_VERSION",
        description="Azure OpenAI API version"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_producer_config(self) -> AgentConfig:
        """Get configuration for the Producer agent."""
        return AgentConfig(
            model_name=self.producer_model,
            temperature=self.producer_temperature
        )
    
    def get_critic_config(self) -> AgentConfig:
        """Get configuration for the Critic agent."""
        return AgentConfig(
            model_name=self.critic_model,
            temperature=self.critic_temperature
        )
    
    def get_orchestrator_config(self) -> OrchestratorConfig:
        """Get configuration for the Orchestrator."""
        return OrchestratorConfig(
            max_iterations=self.max_iterations,
            pass_threshold=self.pass_threshold
        )


# Global configuration instance
# This is loaded once at module import and can be imported throughout the app
config = AppConfig()
