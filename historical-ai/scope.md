# Project Scope: Historically Bounded AI Assistant

## Define Scope
**Knowledge Cutoff**: 31 December 1899
**Operational Mode**: Fully Offline
**User Interaction**: Text-based query and response

## Rules and Constraints
1.  **No Modern Inference**: The system must not use or reference any events, technologies, or concepts introduced after 1899.
2.  **No Internet Access**: The system must run entirely locally without external API calls.
3.  **Refusal Rules**:
    - Any query containing modern keywords (e.g., "internet", "nuclear", "airplane") must be refused.
    - Any query referencing post-1900 dates must be refused.
    - Refusal message: "This knowledge lies beyond the present era and cannot be addressed."

## Accepted Tech Stack
- **Language**: Python
- **ML Frameworks**: HuggingFace Transformers, Sentence-Transformers, PyTorch
- **Vector Database**: FAISS (Local)
- **Orchestration**: Custom Python scripts (or LangChain option)
- **LLM**: Local Open-source LLM (e.g., Llama, Mistral - assuming local weights available)

## Deliverables
- Functional RAG pipeline
- Era-specific guardrails
- Evaluation suite
- Documentation
