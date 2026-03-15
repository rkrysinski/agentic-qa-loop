# Architecture

## The Producer-Critic Loop

Defined in [`app/orchestrator.py`](../app/orchestrator.py):

1. User uploads a document and asks a question
2. **Producer** generates an answer grounded in the document
3. **Critic** evaluates the answer and returns a structured `CritiqueResult`
4. If `PASS` → return final answer. If `FAIL` → feed critique back to Producer and repeat
5. Loop ends on `PASS` or when max iterations is reached

## Critique Rubric

The Critic scores answers on 5 dimensions (0.0–1.0):

| Dimension | Description |
|-----------|-------------|
| Groundedness | Every claim supported by the source document |
| Recall | All relevant information from the document included |
| Precision | Focused, no irrelevant content |
| Logical Consistency | Internally coherent, no contradictions |
| Instruction Following | Directly addresses the question asked |

**Pass criteria**: all scores ≥ `PASS_THRESHOLD` and no HIGH severity issues.

## Project Structure

```
agentic-qa-loop/
├── app/
│   ├── agents.py        # Agent definitions and system prompts
│   ├── config.py        # Pydantic-based configuration
│   ├── orchestrator.py  # Producer-Critic loop
│   ├── schemas.py       # Structured output models
│   └── utils.py         # File extraction utilities
├── main.py              # Chainlit UI entry point
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Tech Stack

- **UI**: [Chainlit](https://github.com/Chainlit/chainlit)
- **Agent framework**: [PydanticAI](https://ai.pydantic.dev/)
- **LLM gateway**: [LiteLLM](https://github.com/BerriAI/litellm)
- **Configuration**: [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
