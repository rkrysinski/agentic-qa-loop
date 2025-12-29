# Agentic Q&A Loop

A multi-agent collaborative Q&A system that uses an adversarial Producer-Critic loop to generate high-accuracy, grounded answers from user-provided documents.

## 🚀 Overview

This system tackles LLM hallucinations by implementing an iterative refinement process with two specialized agents:

1. **Producer Agent**: Synthesizes comprehensive answers from source documents
2. **Critic Agent**: Rigorously evaluates answers against a structured rubric (Groundedness, Recall, Precision, Logical Consistency, Instruction Following)

The system orchestrates a feedback loop where the Critic's structured evaluation guides the Producer's refinements until the answer passes validation or reaches the maximum iteration limit.

## ✨ Features

- **Multi-Agent Architecture**: Decoupled synthesis and auditing roles with specialized prompts
- **Structured Output**: Pydantic-enforced JSON schema for critiques with quantitative scores and actionable feedback
- **Interactive UI**: Built with **Chainlit** - visualize every iteration and agent interaction
- **Chat with your Answer**: Iterate on the final result by asking follow-up questions without re-uploading documents
- **Configurable Settings**: Adjust max iterations via UI slider (1-10 range)
- **Provider Agnostic**: Uses **PydanticAI** + **LiteLLM** to support any LLM provider (Azure OpenAI, OpenAI, Anthropic, Google, etc.)
- **Type-Safe Configuration**: Pydantic-based settings with environment variable support
- **Docker Ready**: Fully containerized for consistent deployment

## 🛠️ Tech Stack

- **Language**: Python 3.12+
- **UI**: [Chainlit](https://github.com/Chainlit/chainlit)
- **Agent Framework**: [PydanticAI](https://ai.pydantic.dev/)
- **LLM Gateway**: [LiteLLM](https://github.com/BerriAI/litellm) via PydanticAI's `LiteLLMProvider`
- **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Infrastructure**: Docker & Docker Compose

## 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- **OR** Python 3.12+ installed locally
- Access to an LLM provider (default: Azure OpenAI)

## ⚙️ Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/agentic-qa-loop.git
cd agentic-qa-loop
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# Azure OpenAI Configuration
AZURE_API_KEY=your_azure_api_key_here
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview

# Model Configuration
PRODUCER_MODEL=azure/gpt-5-mini
PRODUCER_TEMPERATURE=1.0

CRITIC_MODEL=azure/gpt-4o
CRITIC_TEMPERATURE=0.4

# Orchestrator Configuration
MAX_ITERATIONS=3
PASS_THRESHOLD=0.8
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `PRODUCER_MODEL` | LiteLLM model identifier for Producer | `azure/gpt-5-mini` |
| `PRODUCER_TEMPERATURE` | Sampling temperature for Producer | `1.0` |
| `CRITIC_MODEL` | LiteLLM model identifier for Critic | `azure/gpt-4o` |
| `CRITIC_TEMPERATURE` | Sampling temperature for Critic | `0.4` |
| `MAX_ITERATIONS` | Default maximum refinement loops | `3` |
| `PASS_THRESHOLD` | Minimum score for PASS status | `0.8` |

**Note**: You can use any LiteLLM-supported model name (e.g., `gpt-4o`, `claude-3-5-sonnet`, `gemini/gemini-pro`). See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for supported providers.

## 🐳 Running with Docker (Recommended)

Build and start the application:

```bash
docker-compose up --build
```

Access the application at: **[http://localhost:8000](http://localhost:8000)**

To rebuild from scratch:

```bash
docker-compose build --no-cache
docker-compose up
```

## 💻 Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Chainlit application:
   ```bash
   chainlit run main.py -w
   ```
   *(The `-w` flag enables hot-reloading)*

## 🎯 Usage

1. **Start the application** (Docker or local)
2. **Open the UI** at http://localhost:8000
3. **Configure settings** (optional):
   - Click the settings icon
   - Adjust "Maximum Iterations" slider (1-10)
4. **Upload a document** (text file, markdown, etc.)
5. **Ask a question** about the document
6. **Watch the loop**:
   - Producer generates initial answer
   - Critic evaluates with structured feedback
   - Producer refines based on critique
   - Repeat until PASS or max iterations reached
7. **Review the final answer**
8. **Iterate (Optional)**:
   - Ask follow-up questions (e.g., "Make it shorter", "Translate to Spanish")
   - The system will use the *previous answer* as context for further refinement

## 🧩 Architecture

### Project Structure

```
agentic-qa-loop/
├── app/
│   ├── agents.py          # Agent factory methods
│   ├── config.py          # Pydantic-based configuration
│   ├── orchestrator.py    # Producer-Critic loop logic
│   ├── schemas.py         # Pydantic models for structured output
│   └── utils.py           # File extraction utilities
├── main.py                # Chainlit UI entry point
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Service orchestration
└── .env.example           # Environment template
```

### The Orchestration Loop

Defined in [`app/orchestrator.py`](app/orchestrator.py):

1. **Initialization**: User uploads document and asks question
2. **Iteration Loop** (max N times):
   - **Producer Phase**: Generate/refine answer based on document and previous feedback
   - **Critic Phase**: Evaluate answer against rubric, return structured `CritiqueResult`
   - **Decision**:
     - `PASS` → Return final answer
     - `FAIL` → Feed actionable feedback back to Producer
3. **Termination**: Return best answer after max iterations or on PASS

### Agent Configuration

Agents are created via specialized factory methods in [`app/agents.py`](app/agents.py):

```python
# Producer: Synthesizes answers
producer = create_producer_agent(
    model_name="azure/gpt-5-mini",  # Optional override
    temperature=1.0,                 # Optional override
    model_settings={"max_tokens": 2000}  # Optional LiteLLM params
)

# Critic: Evaluates with structured output
critic = create_critic_agent(
    model_name="azure/gpt-4o",
    temperature=0.4,
    model_settings={"top_p": 0.8}
)
```

### Critique Rubric

The Critic evaluates answers on 5 dimensions (0.0-1.0 scale):

| Dimension | Description |
|-----------|-------------|
| **Groundedness** | Every claim supported by source document (no hallucinations) |
| **Recall** | All relevant information from document included |
| **Precision** | Focused, no irrelevant information |
| **Logical Consistency** | Internally coherent, no contradictions |
| **Instruction Following** | Directly addresses the user's question |

**Pass Criteria**: All scores ≥ 0.8 AND no HIGH severity issues

### Structured Output

The system uses Pydantic models ([`app/schemas.py`](app/schemas.py)) to ensure type-safe, validated responses:

```python
class CritiqueResult(BaseModel):
    iteration_metadata: IterationMetadata
    global_status: Literal["PASS", "FAIL"]
    quantitative_scores: QuantitativeScores
    actionable_feedback: List[ActionableFeedback]
    critic_confidence_score: float
```

PydanticAI automatically injects the schema into the LLM prompt and validates responses.

## 🔧 Advanced Customization

### Using Different Models per Agent

```python
# In app/orchestrator.py or custom script
producer = create_producer_agent(model_name="gpt-4o", temperature=1.2)
critic = create_critic_agent(model_name="claude-3-5-sonnet", temperature=0.3)
```

### Adding Custom LiteLLM Parameters

```python
agent = create_producer_agent(
    model_settings={
        "max_tokens": 3000,
        "top_p": 0.95,
        "frequency_penalty": 0.3
    }
)
```

### Changing Providers

Simply update your `.env`:

```env
# Switch to OpenAI
PRODUCER_MODEL=gpt-4o
CRITIC_MODEL=gpt-4o-mini

# Or Anthropic
PRODUCER_MODEL=claude-3-5-sonnet
CRITIC_MODEL=claude-3-5-sonnet

# Or Google
PRODUCER_MODEL=gemini/gemini-pro
CRITIC_MODEL=gemini/gemini-pro
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [PydanticAI](https://ai.pydantic.dev/) for the excellent agent framework
- [LiteLLM](https://github.com/BerriAI/litellm) for unified LLM access
- [Chainlit](https://github.com/Chainlit/chainlit) for the interactive UI
