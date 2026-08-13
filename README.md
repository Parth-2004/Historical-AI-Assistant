# Historically Bounded AI Assistant (1890 Edition)

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Knowledge Cutoff](https://img.shields.io/badge/Knowledge_Cutoff-1899-brown)

## Project Overview
The **Historically Bounded AI Assistant** is an offline Retrieval-Augmented Generation (RAG) system designed to answer questions using **only knowledge available before December 31, 1899**. 

Unlike modern AI models that have access to the internet and 21st-century data, this system is strictly engineered to simulating an intelligent agent existing in the late Victorian era (c. 1890). It features strict **temporal guardrails** that reject any query related to modern technology, ensuring a historically immersive and safe experience.

**Key Definition**: *This is an "Offline-First" AI system suitable for secure environments, academic demonstrations, and resume portfolios.*

---

## Architecture & Concepts

The system follows a modular RAG architecture:

1.  **Era-Specific Guardrails**:
    *   **Concept**: A filtering layer that intercepts user queries *before* they reach the brain of the AI.
    *   **Logic**: Regex-based keyword spotting blocks terms like "Internet", "Nuclear", "iPhone", and post-1900 dates.
    *   **Outcome**: Zero-shot refusal of anachronistic queries.

2.  **Retrieval-Augmented Generation (RAG)**:
    *   **Vector Database (FAISS)**: Stores mathematical representations (embeddings) of historical texts (e.g., *On the Origin of Species*, *Gettysburg Address*).
    *   **Semantic Search**: Finds the most relevant 19th-century text chunks matching the user's query.
    *   **Context Assembly**: Injects these historical facts into the prompt given to the Language Model.

3.  **Offline Inference Engine**:
    *   **Mock Mode (Default Demo)**: A lightweight heuristic engine for standard queries (Newton, Darwin, etc.) generally used for quick demos without downloading 10GB+ models.
    *   **Full ML Mode**: Supports local execution of open-source LLMs (like Llama-2 or Mistral) via HuggingFace Transformers for generating novel text based on retrieved context.

---

## Tech Stack

| Component | Tool / Library | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **Streamlit** | Creates the responsive, parchment-themed web UI. |
| **Language** | **Python 3.9+** | Core logic and orchestration. |
| **Vector DB** | **FAISS (CPU)** | Fast, local similarity search for document chunks. |
| **Embeddings** | **Sentence-Transformers** | Converts text to vectors (Optional/Mock supported). |
| **Validation** | **Regex** | Strict pattern matching for guardrails. |

---

## Supported Use Cases

### What It Answers (The "Happy Path")
The system is optimized for topics well-documented and understood in the 19th Century:
*   **Physics**: "Who is Isaac Newton?", "What is light?", "Explain electricity."
*   **Biology**: "What is natural selection?", "Explain Darwin's theory."
*   **History**: "Who is Abraham Lincoln?", "What happened at Gettysburg?"
*   **General Knowledge**: "What isn't an electron?" (Includes 1897 discovery context).

### What It Refuses (The "Guardrails")
The system will strictly refuse to answer queries containing anachronisms:
*   **Modern Tech**: "What is an iPhone?", "How does WiFi work?"
*   **Future Events**: "Who won the World War?", "What is the United Nations?"
*   **Computing**: "Write a Python script", "What is AI?"

---

## Installation & Usage

### 1. Setup Environment
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Build Knowledge Base
Ingest the raw historical data into the vector database:
```bash
python app/build_knowledge_base.py
```

### 3. Run the Interface
Launch the web UI:
```bash
streamlit run app/ui.py
# Open http://localhost:8501
```

---

## Project Structure

```text
historical-ai/
├── app/
│   ├── main.py                # Core backend logic & CLI entry point
│   ├── ui.py                  # Streamlit frontend code (CSS & Layout)
│   ├── guardrails.py          # Safety filters (keywords & dates)
│   ├── retriever.py           # FAISS vector database wrapper
│   ├── llm.py                 # Offline Model wrapper (Mock & Real modes)
│   └── build_knowledge_base.py # Data ingestion pipeline
├── data/
│   ├── raw/                   # Original text files (Darwin, Lincoln)
│   └── chunks/                # Processed JSON chunks
├── vector_db/                 # Stored FAISS index files
├── evaluation/                # Test suites for guardrails
└── requirements.txt           # Python dependencies
```

---

## Mock vs. Real Mode

*   **Mock Mode (Current Default)**:
    *   Runs instantly without heavy downloads.
    *   Uses a "Dictionary of Knowledge" to answer specific demo questions (Newton, Darwin, etc.).
    *   Provides a generic "Consulting Archives..." response for unknown valid queries.
*   **Real Mode**:
    *   Requires downloading a `.gguf` or HuggingFace model.
    *   Generates organic, word-by-word answers from the LLM.
    *   To enable: Install `torch` and run with `--model_path` argument.

---

> *"The past is a foreign country; they do things differently there."* — L.P. Hartley (1953) [Note: Quote falls outside knowledge cutoff, system would refuse to cite this.]
