# Agentic Q&A Loop

## 🎯 What is this?

An intelligent multi-agent system that generates **high-accuracy, grounded answers** from your documents using an iterative Producer-Critic refinement loop.

## 🚀 How it works

### The Two-Agent System

1. **Producer Agent** 🎨
   - Synthesizes comprehensive answers from your document
   - Incorporates feedback from previous iterations
   - Cites specific sections to ensure grounding

2. **Critic Agent** 🔍
   - Rigorously evaluates answers against a structured rubric
   - Provides quantitative scores (0-100%) across 5 dimensions
   - Generates actionable feedback for improvement

### The Refinement Loop

```
Upload Document → Ask Question
         ↓
    Producer generates answer
         ↓
    Critic evaluates (PASS/FAIL)
         ↓
    ✅ PASS → Return final answer
    ❌ FAIL → Producer refines based on feedback
         ↓
    Repeat until PASS or max iterations reached
         ↓
    ✅ Review & Iterate (ask follow-up questions)
```

## 📊 Evaluation Rubric

The Critic scores answers on 5 dimensions:

| Dimension | What it measures |
|-----------|------------------|
| **🎯 Groundedness** | Every claim supported by the document (no hallucinations) |
| **📚 Recall** | All relevant information included |
| **✂️ Precision** | Focused, no irrelevant content |
| **🧩 Logical Consistency** | Internally coherent, no contradictions |
| **📝 Instruction Following** | Directly addresses your question |

**Pass Criteria:** All scores ≥ 80% AND no high-severity issues

## ⚙️ Settings

Click the **settings icon** (⚙️) to configure:

- **Maximum Iterations** (1-10): How many refinement loops to allow
  - Default: 3 iterations
  - Higher = more refinement, but slower
  - Lower = faster, but potentially less polished

## 💡 Tips for Best Results

1. **Upload clear documents**: Text files, Markdown, or PDFs work best
2. **Ask specific questions**: "What are the key findings?" is better than "Summarize this"
2. **Ask specific questions**: "What are the key findings?" is better than "Summarize this"
3. **Iterate**: Don't like the answer? Ask the system to "Make it shorter" or "Focus on cost" (it remembers context!)
4. **Watch the iterations**: See how the answer improves with each cycle
5. **Review the scores**: Understand where the answer excels or needs work

## 🔧 Technical Details

- **Framework**: PydanticAI for type-safe agent orchestration
- **LLM Gateway**: LiteLLM for provider-agnostic model access
- **Structured Output**: Pydantic models ensure valid, parseable critiques
- **UI**: Chainlit for interactive, step-by-step visualization

## 📖 Example Use Cases

- **Research Analysis**: Extract insights from academic papers
- **Document Q&A**: Answer questions about contracts, reports, manuals
- **Content Verification**: Ensure summaries are accurate and complete
- **Knowledge Extraction**: Pull specific information from large documents

---

**Ready to start?** Upload a document and ask your question! 🚀
