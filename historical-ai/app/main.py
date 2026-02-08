import argparse
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.guardrails import validate_query, validate_response
from app.retriever import Retriever
from app.llm import HistoricalLLM
from app.prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Global instances for reuse
retriever = None
llm = None
initialized = False
current_model_path = None

def initialize_system(model_path="mock"):
    global retriever, llm, initialized, current_model_path
    
    # Only skip if already initialized AND with the same model
    if initialized and current_model_path == model_path:
        return

    print(f"Initializing System (1890 Mode)... [Model: {model_path}]")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vector_db_path = os.path.join(base_dir, "vector_db")
    
    try:
        retriever = Retriever(vector_db_path)
    except Exception as e:
        print(f"Error initializing retriever: {e}")
        # Construct a dummy retriever if DB missing to prevent crash on import, 
        # though functionality will be broken.
        retriever = None

    llm = HistoricalLLM(model_path=model_path)
    current_model_path = model_path
    initialized = True

def ask_historical_ai(query: str, model_path="mock") -> dict:
    """
    Process a query through the historical RAG pipeline.
    Returns:
    {
      "status": "ok" | "refused" | "error",
      "answer": str,
      "sources": list (optional)
    }
    """
    if not initialized:
        initialize_system(model_path)

    # 1. Guardrails
    if not validate_query(query):
        return {
            "status": "refused",
            "answer": "This knowledge lies beyond the present era and cannot be addressed.",
            "sources": []
        }

    try:
        if not retriever:
            return {
                "status": "error",
                "answer": "System Error: Knowledge base not found. Please run build_knowledge_base.py.",
                "sources": []
            }

        # 2. Retrieval
        results = retriever.retrieve(query)
        context_text = ""
        sources = []
        
        if results:
            context_text = retriever.format_context(results)
            # transform results to simple source list
            sources = [f"{r['title']} ({r['year']})" for r in results]
        else:
            context_text = "No specific records found."

        # 3. Prompt Assembly
        user_prompt = USER_PROMPT_TEMPLATE.format(
            retrieved_historical_text=context_text,
            user_query=query
        )

        # 4. Generation
        response = llm.generate(SYSTEM_PROMPT, user_prompt)

        # 5. Output Validation
        if not validate_response(response):
             return {
                 "status": "refused",
                 "answer": "[REDACTED - ANACHRONISM DETECTED IN OUTPUT]",
                 "sources": sources
             }
             
        return {
            "status": "ok",
            "answer": response,
            "sources": sources
        }
        
    except Exception as e:
        return {
            "status": "error",
            "answer": f"An internal error occurred: {str(e)}",
            "sources": []
        }

def main():
    parser = argparse.ArgumentParser(description="Historically Bounded AI")
    parser.add_argument("--query", type=str, help="User query")
    parser.add_argument("--model_path", type=str, default="mock", help="Path to local LLM")
    args = parser.parse_args()

    # Pre-initialize
    initialize_system(args.model_path)

    def process_query_cli(query):
        print(f"\nQuery: {query}")
        result = ask_historical_ai(query, args.model_path)
        
        if result["status"] == "refused":
            print(f"Response: {result['answer']}")
        elif result["status"] == "error":
            print(f"Error: {result['answer']}")
        else:
            print(f"Debug: Retrieved sources: {result['sources']}")
            print(f"Final Answer:\n{result['answer']}")

    if args.query:
        process_query_cli(args.query)
    else:
        while True:
            try:
                q = input("\nEnter query (or 'exit'): ")
                if q.lower() == 'exit':
                    break
                process_query_cli(q)
            except KeyboardInterrupt:
                break
    print("Exiting.")

if __name__ == "__main__":
    main()
