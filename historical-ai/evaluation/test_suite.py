import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.guardrails import validate_query
from app.retriever import Retriever
from app.main import ask_historical_ai

def load_test_cases():
    test_cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(test_cases_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_tests():
    TEST_CASES = load_test_cases()
    print("Running Evaluation Suite...")
    passed = 0
    total = len(TEST_CASES)

    for case in TEST_CASES:
        q = case["query"]
        expected = case["expected"]

        is_valid = validate_query(q)
        result = "Allowed" if is_valid else "Refusal"

        if result == expected:
            print(f"[PASS] Query: '{q}' -> {result}")
            passed += 1
        else:
            print(f"[FAIL] Query: '{q}' -> Got {result}, Expected {expected}")

    print(f"\nResults: {passed}/{total} passed.")

    # Check Retriever (Integration Test)
    # Only run if vector db exists (metadata file is best indicator)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vector_db = os.path.join(base_dir, "vector_db")
    if os.path.exists(os.path.join(vector_db, "chunks_metadata.json")):
        print("\nTesting Retriever Connectivity and Thresholds...")
        try:
            retriever = Retriever(vector_db)
            print("[PASS] Retriever loaded successfully.")

            # Test Irrelevant Retrieval
            irrelevant_query = "What is the recipe for chocolate chip cookies?"
            irrelevant_results = retriever.retrieve(irrelevant_query, k=3)
            if len(irrelevant_results) == 0:
                print("[PASS] Irrelevant query successfully filtered out.")
            else:
                print(f"[FAIL] Irrelevant query returned {len(irrelevant_results)} chunks (Expected 0).")

            # Test Relevant Retrieval
            relevant_query = "What is natural selection?"
            relevant_results = retriever.retrieve(relevant_query, k=1)
            if len(relevant_results) > 0:
                print("[PASS] Relevant query successfully retrieved context.")
            else:
                print("[FAIL] Relevant query returned 0 chunks (Expected > 0).")

            # Test Threshold Limits
            threshold_query = "Who gave the Gettysburg address?"
            threshold_results = retriever.retrieve(threshold_query, k=1)
            if len(threshold_results) > 0:
                print("[PASS] Borderline relevant query successfully retrieved context.")
            else:
                print("[FAIL] Borderline relevant query returned 0 chunks (Expected > 0).")

            # Test Duplicate Removal
            if len(retriever.metadata) > 0:
                original_metadata = retriever.metadata.copy()
                original_is_mock = retriever.is_mock
                retriever.is_mock = True  # use mock for controlled deduplication test
                # Inject a duplicate
                retriever.metadata.append(retriever.metadata[0])
                dup_results = retriever.retrieve(retriever.metadata[0]['title'], k=3)
                texts = [r['text'] for r in dup_results]

                # Restore original to not mess with subsequent tests
                retriever.metadata = original_metadata
                retriever.is_mock = original_is_mock

                if len(texts) == len(set(texts)):
                    print("[PASS] Retriever successfully deduplicates identical text chunks.")
                else:
                    print(f"[FAIL] Retriever returned duplicate text chunks. Got {len(texts)} chunks, but only {len(set(texts))} unique.")

        except Exception as e:
            print(f"[FAIL] Retriever test failed: {e}")
    else:
        print("\n[SKIP] Retriever test skipped (DB not built).")

    # Test Chunk Length
    chunks_file = os.path.join(base_dir, "data", "chunks", "chunks.json")
    if os.path.exists(chunks_file):
        print("\nTesting Chunk Sizes...")
        try:
            import json
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            max_seq_length = model.max_seq_length

            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)

            oversized_chunks = 0
            for i, chunk in enumerate(chunks):
                tokens = model.tokenizer.tokenize(chunk["text"])
                if len(tokens) > max_seq_length:
                    oversized_chunks += 1

            if oversized_chunks == 0:
                print(f"[PASS] All {len(chunks)} chunks are within the max sequence length of {max_seq_length} tokens.")
            else:
                print(f"[FAIL] {oversized_chunks} chunks exceed the max sequence length of {max_seq_length} tokens.")
        except Exception as e:
            print(f"[SKIP] Chunk size test failed to run: {e}")
    else:
        print("\n[SKIP] Chunk size test skipped (chunks.json not found).")

    print("\nTesting End-to-End Mock LLM Grounding...")
    try:
        query = "Who gave the Gettysburg address?"
        result = ask_historical_ai(query, model_path="mock")
        if result["status"] == "ok" and "Based on the historical archive:" in result["answer"]:
            print(f"[PASS] Mock LLM correctly used retrieved context for query: '{query}'")
        else:
            print(f"[FAIL] Mock LLM did not use retrieved context. Answer: {result.get('answer')}")
    except Exception as e:
        print(f"[FAIL] Mock LLM Grounding test failed: {e}")


if __name__ == "__main__":
    run_tests()
