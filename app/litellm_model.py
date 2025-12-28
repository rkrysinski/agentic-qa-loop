from typing import Optional, List, Any
import datetime
from pydantic_ai.models import Model, ModelRequestParameters
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ModelRequest, UserPromptPart, SystemPromptPart, ModelResponsePart
import litellm

class LiteLLMModel(Model):
    """
    A custom PydanticAI Model that uses LiteLLM for completions.
    This allows us to support any provider that LiteLLM supports (Azure, OpenAI, etc.)
    without relying on specific provider clients.
    """
    
    def __init__(self, model_name: str):
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def system(self) -> str:
        return "litellm"

    async def request(
        self, 
        messages: List[ModelMessage], 
        model_settings: Optional[Any], 
        model_request_parameters: ModelRequestParameters
    ) -> ModelResponse:
        
        # Convert PydanticAI messages to LiteLLM/OpenAI format
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, ModelRequest):
                for part in msg.parts:
                    if isinstance(part, SystemPromptPart):
                        openai_messages.append({"role": "system", "content": part.content})
                    elif isinstance(part, UserPromptPart):
                        openai_messages.append({"role": "user", "content": part.content})
            elif isinstance(msg, ModelResponse):
                # For history, we need to map back response parts
                for part in msg.parts:
                    if isinstance(part, TextPart):
                         openai_messages.append({"role": "assistant", "content": part.content})

        # Call LiteLLM
        response = await litellm.acompletion(
            model=self.model_name,
            messages=openai_messages,
            temperature=1 # Default, or extract from model_settings if available
        )
        
        # Convert response back to ModelResponse
        content = response.choices[0].message.content
        
        return ModelResponse(
            parts=[TextPart(content=content)],
            timestamp=datetime.datetime.now(),
            model_name=self.model_name
        )
