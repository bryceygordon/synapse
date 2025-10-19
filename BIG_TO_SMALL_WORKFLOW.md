# Big-to-Small Model Delegation Workflow

**Purpose**: To significantly reduce token costs on large or repetitive tasks by using expensive, powerful models for planning and cheap, fast models for execution.
**Status**: DRAFT
**Owner**: Synapse AI Orchestration Engine

---

## 🎯 Core Philosophy

**Use the right tool for the job.** Don't use a sledgehammer (a powerful, expensive model like Claude 3.5 Sonnet) to crack a nut (a small, well-defined task).

-   **Expensive Models (e.g., Sonnet):** Excel at reasoning, planning, and understanding complex problems. Use them for the initial analysis and breaking down large tasks.
-   **Cheap Models (e.g., Haiku, GPT-4o-mini):** Excel at executing precise, well-defined instructions with minimal context. Use them for the actual implementation of small tasks.

---

## 📊 The Workflow

This workflow consists of three distinct phases:

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Planning (Claude 3.5 Sonnet - Expensive)      │
│ - Analyze the user's request                               │
│ - Explore the codebase to gather context                   │
│ - Formulate a detailed, step-by-step implementation plan │
│ - Decompose the plan into 5-10 specific mini-tasks       │
│ - Generate a precise specification for each mini-task      │
│ Cost: ~50,000 tokens ($0.15)                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Execution (Haiku or GPT-4o-mini - Cheap)      │
│ - Execute mini-task #1 based on its spec (2,000 tokens)    │
│ - Execute mini-task #2 based on its spec (2,000 tokens)    │
│ - ... (repeat for all remaining tasks)                     │
│ Cost: 10 × 2,000 = 20,000 tokens ($0.02 with Haiku)      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Verification (Claude 3.5 Sonnet - Expensive)  │
│ - Review all the code changes made by the small models     │
│ - Run integration tests to ensure correctness            │
│ - Commit the final, verified changes to the repository     │
│ Cost: ~15,000 tokens ($0.045)                           │
└─────────────────────────────────────────────────────────┘
```

**Total Cost:** ~$0.22 (vs. ~$0.50+ doing everything with Sonnet)
**Projected Savings:** **50-60%** on large tasks.

---

## ✅ When to Use This Pattern

This pattern is ideal for tasks that are:
-   **Large-scale:** Like refactoring a 3,000-line file into multiple smaller files.
-   **Repetitive:** Like compressing 50 docstrings or renaming a variable across 20 files.
-   **Well-defined:** Like generating a suite of 10 test cases based on a clear specification.
-   **Parallelizable:** When multiple small tasks can be worked on independently.

---

## ❌ When NOT to Use This Pattern

Avoid this pattern for tasks that require:
-   **Deep Reasoning:** Architectural decisions or designing a new, complex algorithm.
-   **Exploratory Work:** When the solution is not clear and requires iterative exploration and debugging.
-   **Complex Debugging:** When a bug's root cause is unknown and requires a deep understanding of the entire system.

In these cases, the context-switching and overhead of creating mini-tasks will be less efficient than using a single powerful model.

---

## 📝 Mini-Task Specification Format

A high-quality specification is the key to success with small models. It must be precise, unambiguous, and require zero exploration from the execution agent.

Use the template in `TASK_TEMPLATES.md` to structure your mini-tasks.

---

## 🚀 How to Implement

1.  **Identify a suitable task.** (e.g., "Split the `todoist.py` file.")
2.  **Use a powerful model (Sonnet) for Phase 1.** Create the detailed breakdown and generate the mini-task specification files. A good starting point is `SPLIT_TODOIST_MINI_PROJECTS.md`.
3.  **Use a cheap model (Haiku) for Phase 2.** Execute the first mini-task to validate the process.
4.  **Iterate.** Continue executing the mini-tasks.
5.  **Use a powerful model (Sonnet) for Phase 3.** Review, test, and commit the final result.
6.  **Update the status.** Mark the relevant tasks as complete in `TOKEN_OPTIMIZATION_STATUS.md`.
