# Agentic Q&A Loop

A multi-agent system that generates accurate, document-grounded answers using an iterative Producer-Critic loop.

```
 Document + Question
        │
        ▼
   ┌─────────┐
   │ Producer│◄──── Critique feedback
   └────┬────┘
        │ Answer
        ▼
   ┌─────────┐
   │  Critic │──── PASS ──► Final Answer
   └─────────┘
        │
       FAIL (repeat up to N iterations)
```

## Installation

```bash
cp .env.example .env   # add your API keys
docker-compose up --build
```

Open **http://localhost:8000**

## Usage

1. Upload a document
2. Ask a question
3. Watch the Producer generate an answer and the Critic refine it until it passes validation

Follow-up questions are supported — the system uses the previous answer as context.

## Documentation

- [Configuration](docs/configuration.md) — environment variables and model settings
- [Architecture](docs/architecture.md) — how the Producer-Critic loop works

## License

MIT
