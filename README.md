# Agentic Q&A Loop

A multi-agent system that generates accurate, document-grounded answers using an iterative Producer-Critic loop.

Upload a document, ask a question, and get a grounded answer. Once the final answer is ready, ask follow-up questions about **that answer** — to reformat, translate, shorten, or expand it. The document is not re-analysed; the follow-up refines the answer itself.

![demo](demo/demo.gif)

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


## Documentation

- [Configuration](docs/configuration.md) — environment variables and model settings
- [Architecture](docs/architecture.md) — how the Producer-Critic loop works

## License

MIT
