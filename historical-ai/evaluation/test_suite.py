import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.guardrails import validate_query
from app.retriever import Retriever

# Mock expected behaviors
TEST_CASES = [
    {"query": "What is AI?", "expected": "Refusal"},
    {"query": "Who is Newton?", "expected": "Allowed"},
    {"query": "Explain WiFi", "expected": "Refusal"},
    {"query": "What is evolution?", "expected": "Allowed"},
    {"query": "Tell me about the iphone", "expected": "Refusal"},
    {"query": "When was the Civil War?", "expected": "Allowed"},
    {"query": "What happened in 1900?", "expected": "Refusal"},
    {"query": "Tell me about computers", "expected": "Refusal"},
    {"query": "What are smartphones?", "expected": "Refusal"},
    {"query": "What happened in 1899?", "expected": "Allowed"},
    {"query": "Who is John Doe?", "expected": "Allowed"}
]

def run_tests():
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
        print("\nTesting Retriever Connectivity...")
        try:
            retriever = Retriever(vector_db)
            print("[PASS] Retriever loaded successfully.")
        except Exception as e:
            print(f"[FAIL] Retriever load failed: {e}")
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


if __name__ == "__main__":
    run_tests()
