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

        # Prepare litellm kwargs
        litellm_kwargs = {
            "model": self.model_name,
            "messages": openai_messages,
            "temperature": 1  # Default, or extract from model_settings if available
        }
        
        # Handle structured output if requested
        if model_request_parameters.output_object is not None:
            # PydanticAI wants structured output
            # Use response_format for JSON mode with schema
            output_def = model_request_parameters.output_object
            
            # Get the schema and ensure it has additionalProperties: false everywhere
            # (required by Azure's strict mode)
            schema = output_def.json_schema.copy()
            schema = self._ensure_no_additional_properties(schema)
            
            # For OpenAI-compatible APIs (including Azure), use response_format with json_schema
            litellm_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_def.name or "output",
                    "schema": schema,
                    "strict": True
                }
            }

        # Call LiteLLM
        response = await litellm.acompletion(**litellm_kwargs)
        
        # Convert response back to ModelResponse
        content = response.choices[0].message.content
        
        return ModelResponse(
            parts=[TextPart(content=content)],
            timestamp=datetime.datetime.now(),
            model_name=self.model_name
        )
    
    def _ensure_no_additional_properties(self, schema: dict) -> dict:
        """
        Recursively ensure all objects in the schema have additionalProperties: false
        and all properties are in the required array.
        This is required by Azure's structured output API strict mode.
        """
        if isinstance(schema, dict):
            # If this is an object type, add additionalProperties: false
            if schema.get("type") == "object":
                schema["additionalProperties"] = False
                
                # Ensure all properties are in the required array (Azure strict mode requirement)
                if "properties" in schema:
                    all_props = list(schema["properties"].keys())
                    schema["required"] = all_props
            
            # Recursively process all nested schemas
            for key, value in schema.items():
                if isinstance(value, dict):
                    schema[key] = self._ensure_no_additional_properties(value)
                elif isinstance(value, list):
                    schema[key] = [
                        self._ensure_no_additional_properties(item) if isinstance(item, dict) else item
                        for item in value
                    ]
        
        return schema
