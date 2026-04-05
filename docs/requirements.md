# Specification: Multi-Agent Collaborative Q&A System
**Version:** 1.0

---
## 1. Objective
To define a system where a user-provided document and query are processed through an iterative, multi-agent adversarial loop. The goal is to produce a comprehensive, high-accuracy response that has been stress-tested for hallucinations, logical fallacies, and omissions by a secondary model with a different underlying architecture.

---
## 2. System Actors

### 2.1 The Producer Agent
* **Role:** Lead Synthesizer.
* **Responsibility:** Primary analysis of the source document and generation of the initial and refined answers.
* **Constraint:** Must prioritize depth and narrative coherence.

### 2.2 The Critic Agent
* **Role:** Auditor and Fact-Checker.
* **Responsibility:** Evaluating the Producer’s output against the source document using a standardized rubric.
* **Constraint:** Must run on a different LLM architecture than the Producer to minimize shared bias.

### 2.3 The Orchestrator (System Logic)
* **Role:** Traffic Controller.
* **Responsibility:** Managing the hand-offs, tracking version history, and determining when the "Termination Condition" is met.

---
## 3. Functional Workflow

### 3.1 Phase I: Input & Contextualization
* **Input:** User provides a Document ($D$) and a Question ($Q$).
* **Context:** Both agents are granted access to the full context of $D$.

### 3.2 Phase II: Initial Synthesis
* The **Producer** generates a draft answer ($A_1$) based on $D$ and $Q$.
* The draft must cite specific sections of the document to ensure grounding.

### 3.3 Phase III: The Critique Loop
* The **Critic** receives $D$, $Q$, and $A_1$.
* The Critic applies the **Critique Rubric** (see Section 4) and outputs the result in a **Standardized Communication Schema** (see Section 5).
* If the evaluation fails to meet the quality threshold, the feedback is sent back to the Producer.

### 3.4 Phase IV: Refinement & Delivery
* The **Producer** receives the critique and generates a refined answer ($A_n$).
* The cycle repeats until the Orchestrator triggers termination.

---
## 4. The Critique Rubric
The Critic Agent must evaluate every response against the following five dimensions. For each dimension, the Critic provides a score and a specific "Actionable Fix."

| Dimension | Evaluation Criteria |
| :--- | :--- |
| **Groundedness** | Are all claims supported by $D$? Identify any "hallucinations" or external knowledge not present in the source. |
| **Recall (Completeness)** | Does the answer omit critical information from $D$ that is relevant to $Q$? |
| **Precision** | Does the answer include "fluff" or irrelevant information that distracts from the core answer? |
| **Logical Consistency** | Are there internal contradictions in the answer? Does the conclusion follow the premises provided in the text? |
| **Instruction Following** | Does the response adhere to the user's specific constraints (e.g., tone, length, format)? |

> **Note:** The Critic must provide a binary "Pass/Fail" for the Groundedness dimension. A "Fail" here triggers an automatic mandatory revision.

---
## 5. Standardized Communication Schema
To ensure the Orchestrator and Producer can act on the Critic's feedback, the Critic must output its evaluation in a structured format. This schema defines the mandatory data points required for every critique iteration:

```json
{
  "iteration_metadata": {
    "iteration_id": "integer",
    "timestamp": "ISO-8601 string"
  },
  "global_status": "PASS | FAIL",
  "quantitative_scores": {
    "groundedness": "float (0.0 - 1.0)",
    "recall": "float (0.0 - 1.0)",
    "precision": "float (0.0 - 1.0)",
    "logical_consistency": "float (0.0 - 1.0)",
    "instruction_following": "float (0.0 - 1.0)"
  },
  "actionable_feedback": [
    {
      "dimension": "string",
      "severity": "LOW | MEDIUM | HIGH",
      "issue_description": "string",
      "actionable_fix": "string",
      "reference_snippets": ["string"]
    }
  ],
  "critic_confidence_score": "float (0.0 - 1.0)"
}
```

## 6. Requirements for Model Diversity
To ensure the robustness of the feedback loop, the system must adhere to:
1. **Heterogeneous Architectures:** If the Producer uses a Transformer-based model from Provider A, the Critic must use a model from Provider B (e.g., varying training data and RLHF methodologies).
2. **Independent System Prompts:** The Critic’s instructions must emphasize skepticism and "red-teaming," whereas the Producer’s instructions emphasize synthesis and helpfulness.

---
## 7. Termination Conditions
The loop shall terminate under any of the following conditions:
- **Consensus:** The Critic provides a "Pass" across all Rubric dimensions.
- **Stagnation:** The delta between the current answer ($A_n$) and the previous answer ($A_{n-1}$) falls below a significance threshold, indicating no further improvement is likely.
- **Exhaustion:** The system reaches a maximum of $N$ iterations (default $N=3$).

---
## 8. Success Metrics
- **Factuality Rate:** The ratio of verified claims to total claims in the final output.
- **Error Capture Rate:** The number of revisions triggered by the Critic that resulted in a factual correction.
- **User Satisfaction:** Qualitative measure of the "comprehensiveness" of the final answer compared to a single-pass system.