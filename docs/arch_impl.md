# System Architecture and Implementation Plan
Version: 1.0

---
### 1. Executive Summary

This document outlines the implementation strategy for an agentic Q&A system. The architecture leverages **PydanticAI** for structured agentic reasoning, the **LiteLLM Python SDK** for model-agnostic provider integration, and **Chainlit** for an interactive, step-visualized web interface. The system is designed to be fully containerized via **Docker**, facilitating seamless deployment and local experimentation across Azure, OpenAI, and Google Gemini models.

---
### 2. Technical Stack

|**Layer**|**Component**|**Description**|
|---|---|---|
|**User Interface**|**Chainlit**|Python-native UI for chat, document uploads, and multi-step reasoning visualization.|
|**Agent Logic**|**PydanticAI**|Provides type-safe agent definitions and native integration with Pydantic for result validation.|
|**Model Gateway**|**LiteLLM SDK**|A programmatic translation layer that allows switching between providers using standardized model strings.|
|**Data Validation**|**Pydantic v2**|Enforces the "Critique Rubric" schema during agent hand-offs.|
|**Runtime**|**Docker**|Ensures environment consistency across local and cloud-based development.|

---
### 3. System Architecture
The architecture follows a modular pattern where the **Orchestrator** acts as the central state machine.
#### 3.1 Component Interaction
1. **Ingestion:** User uploads a document via Chainlit.
2. **Orchestration:** The Orchestrator initiates a `while` loop, invoking the **Producer Agent** to synthesize an answer.
3. **Critique:** The output is passed to the **Critic Agent**, which returns a structured Pydantic object based on the defined Rubric.
4. **Feedback Loop:** If the "Status" is `FAIL`, the Orchestrator feeds the critique back to the Producer for a refined version.
5. **Visualization:** Every agent "turn" is captured as a `cl.Step` in the UI, allowing the user to expand and inspect the iteration history.
---
### 4. File Structure
```plaintext
/collaborative-qa
├── app/
│   ├── __init__.py
│   ├── agents.py          # PydanticAI Agent definitions + LiteLLM SDK config
│   ├── orchestrator.py    # Recursive/Iterative logic and termination checks
│   ├── schemas.py         # Shared Pydantic Models (CritiqueSchema, etc.)
│   └── utils.py           # Document text extraction (PDF/Docx)
├── .env                   # API Keys (AZURE_API_KEY, GEMINI_API_KEY, etc.)
├── main.py                # Chainlit Entry Point & UI Lifecycle
├── Dockerfile             # Unified Python environment
├── docker-compose.yml     # Service definitions & volume mapping
└── requirements.txt       # Dependencies (pydantic-ai, litellm, chainlit, etc.)
```

---
### 5. Core Implementation Snippets
#### 5.1 Model Agnosticism via LiteLLM SDK
Instead of a separate proxy container, the LiteLLM SDK is used within `agents.py` to route requests dynamically.
```python
# app/agents.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
import os

def create_agent(model_key: str, system_prompt: str, result_type=None):
    # LiteLLM SDK handles the provider translation (Azure, Gemini, OpenAI)
    # We use OpenAIChatModel as the generic wrapper
    model_name = os.getenv(model_key) 
    model = OpenAIChatModel(model_name=model_name)
    
    return Agent(model, system_prompt=system_prompt, result_type=result_type)
```

#### 5.2 Docker Configuration
A single container strategy is used to keep the implementation lean and maintainable.
```yml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - .:/app
    environment:
      - WATCHFILES_FORCE_POLLING=true # For hot-reloading in Docker
```

---
### 6. Execution Workflow
1. **Initialization:** The system loads environment variables to map `PRODUCER_MODEL` and `CRITIC_MODEL`.
2. **Interaction:** Chainlit listens for `on_message` events containing text and document elements.
3. **Iteration:** The Orchestrator manages up to $N$ iterations (per Spec 0.4), logging each to the Chainlit context.
4. **Termination:** The loop exits on a `PASS` status, `Stagnation`, or `Exhaustion`.
## 7. Containerization Strategy (Dockerfile)
To ensure environment parity and security, the system is packaged as a single-process container. A slim Debian-based Python image is used to balance image size with the presence of essential system libraries.

```Dockerfile
# Use a slim version of Python 3.12 for a small, secure footprint
FROM python:3.12-slim

# Set environment variables to optimize Python for containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-privileged user for security (Decision: Avoid running as root)
RUN useradd -m appuser
USER appuser

# Chainlit default port
EXPOSE 8000

# Healthcheck to monitor the status of the web server
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Launch the application using Chainlit
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```