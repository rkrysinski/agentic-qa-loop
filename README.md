# Agentic Q&A Loop

A multi-agent collaborative Q&A system that utilizes an adversarial Producer-Critic loop to generate high-accuracy, grounded answers from user-provided documents.

## 🚀 Overview

This system tackles the problem of "one-shot" LLM hallucinations by implementing an iterative refinement process. Instead of accepting the first answer, the system employs two specialized agents:
1.  **Producer Agent**: Responsible for synthesizing answers and incorporating feedback found in the document.
2.  **Critic Agent**: Responsible for auditing the Producer's output against a strict **Critique Rubric** (Groundedness, Recall, Precision, Logical Consistency).

The system orchestrates a hand-off loop where the Critic's structured feedback is fed back into the Producer until the answer passes validation or iteration limits are reached.

## ✨ Features

-   **Multi-Agent Architecture**: Decoupled synthesis and auditing roles.
-   **Structured Feedback**: Uses Pydantic to enforce a strict JSON schema for critiques (scores + actionable fixes).
-   **Step-by-Step Visualization**: Interactive UI built with **Chainlit** that shows every agent thought process and iteration.
-   **Model Agnostic**: Built on **LiteLLM** and **PydanticAI**, capable of swapping underlying models (Azure OpenAI, Google Gemini, Anthropic, etc.) via configuration.
-   **Docker Ready**: Fully containerized environment for consistent deployment.

## 🛠️ Tech Stack

-   **Language**: Python 3.12+
-   **UI**: [Chainlit](https://github.com/Chainlit/chainlit)
-   **Agent Framework**: [PydanticAI](https://github.com/pydantic/pydantic-ai)
-   **LLM Gateway**: [LiteLLM](https://github.com/BerriAI/litellm)
-   **Infrastructure**: Docker & Docker Compose

## 📋 Prerequisites

To run this project, you will need:
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
-   **OR** Python 3.12+ installed locally
-   Access to an LLM Provider (Default: Azure AI Foundry)

## ⚙️ Configuration

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/agentic-qa-loop.git
    cd agentic-qa-loop
    ```

2.  **Environment Setup**:
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

    Open `.env` and populate your API keys. The default configuration uses Azure OpenAI models:
    ```env
    AZURE_API_KEY=your_key_here
    AZURE_API_BASE=https://your-resource.openai.azure.com/
    AZURE_API_VERSION=2024-02-15-preview
    PRODUCER_MODEL=azure/gpt-4o
    CRITIC_MODEL=azure/gpt-4o-mini
    ```

## 🐳 Running with Docker (Recommended)

Build and start the services:

```bash
docker-compose up --build
```

Access the application at: **[http://localhost:8000](http://localhost:8000)**

## 💻 Running Locally

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the Chainlit application:
    ```bash
    chainlit run main.py -w
    ```
    *(The `-w` flag enables hot-reloading)*

## 🧩 Architecture Details

### The Orchestration Loop
The logic is defined in `app/orchestrator.py`:
1.  **Ingestion**: User uploads a file.
2.  **Phase 1 (Production)**: Producer Agent generates a draft.
3.  **Phase 2 (Critique)**: Critic Agent scores the draft.
4.  **Decision**:
    -   If **PASS**: Return final answer.
    -   If **FAIL**: Feed specific `actionable_feedback` back to Producer for Refinement.
    -   Repeat until `max_iterations` (default: 3).

### Schemas
The system relies on strict typing defined in `app/schemas.py`. The Critic *must* return a `CritiqueResult` object, ensuring the Orchestrator always can parse the pass/fail status and feedback items programmatically.

## 🤝 Contributing

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request
