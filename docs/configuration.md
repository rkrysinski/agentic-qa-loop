# Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```env
GOOGLE_API_KEY=<your_key>
PRODUCER_MODEL=gemini-2.5-pro
PRODUCER_TEMPERATURE=1.0

OPENAI_API_KEY=<your_key>
CRITIC_MODEL=gpt-4o
CRITIC_TEMPERATURE=0.2

MAX_ITERATIONS=8
PASS_THRESHOLD=0.9
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PRODUCER_MODEL` | LiteLLM model identifier for the Producer | `gemini-2.5-pro` |
| `PRODUCER_TEMPERATURE` | Sampling temperature for the Producer | `1.0` |
| `CRITIC_MODEL` | LiteLLM model identifier for the Critic | `gpt-4o` |
| `CRITIC_TEMPERATURE` | Sampling temperature for the Critic | `0.2` |
| `MAX_ITERATIONS` | Maximum refinement loops | `8` |
| `PASS_THRESHOLD` | Minimum score for PASS status | `0.9` |

Any [LiteLLM-supported model](https://docs.litellm.ai/docs/providers) can be used (e.g. `claude-3-5-sonnet`, `gpt-4o`, `gemini-2.5-pro`).

## Azure OpenAI

Use `.env.azure` (see `.env.example` for the template) and set:

```env
AZURE_API_KEY=...
AZURE_API_BASE=https://<your-resource>.openai.azure.com/openai/v1/
```

## Running Locally (without Docker)

```bash
pip install -r requirements.txt
chainlit run main.py -w
```
