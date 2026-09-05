import os
import json
import numpy as np
import re
from typing import List, Dict

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class Retriever:
    def __init__(self, vector_db_dir: str):
        self.vector_db_dir = vector_db_dir
        self.index_path = os.path.join(vector_db_dir, "index.faiss")
        self.meta_path = os.path.join(vector_db_dir, "chunks_metadata.json")
        self.mock_flag = os.path.join(vector_db_dir, "mock_mode.flag")

        self.is_mock = False
        if os.path.exists(self.mock_flag) or not ML_AVAILABLE:
            self.is_mock = True
            print("Retriever running in Mock/Keyword Mode.")
        else:
            if not os.path.exists(self.index_path):
                 raise FileNotFoundError("Vector DB not found.")
            self.index = faiss.read_index(self.index_path)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        if not os.path.exists(self.meta_path):
            raise FileNotFoundError("Metadata not found.")

        with open(self.meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        if self.is_mock:
            # Simple keyword matching for demo with basic stopword filtering
            import string
            stopwords = {'what', 'is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'for', 'with', 'on', 'how', 'why', 'who', 'where', 'when', 'did', 'does', 'do', 'are', 'was', 'were'}

            # Clean and filter query terms
            raw_terms = query.lower().split()
            query_terms = []
            for term in raw_terms:
                cleaned_term = term.strip(string.punctuation)
                if cleaned_term and cleaned_term not in stopwords:
                    query_terms.append(cleaned_term)

            # Fallback in case all words were filtered out
            if not query_terms:
                 query_terms = [t.strip(string.punctuation) for t in raw_terms if t.strip(string.punctuation)]

            scored_results = []
            for item in self.metadata:
                score = 0
                text_lower = item['text'].lower()
                for term in query_terms:
                    # Look for word boundaries to improve accuracy in mock mode
                    if re.search(rf'\b{re.escape(term)}\b', text_lower):
                        score += 1
                if score > 0:
                    scored_results.append((score, item))

            # Sort by score descending
            scored_results.sort(key=lambda x: x[0], reverse=True)

            # Deduplicate by text
            results = []
            seen_texts = set()
            for score, item in scored_results:
                if item['text'] not in seen_texts:
                    seen_texts.add(item['text'])
                    results.append(item)
                    if len(results) >= k:
                        break
            return results
        else:
            query_vector = self.model.encode([query]).astype('float32')
            faiss.normalize_L2(query_vector)

            # Fetch more candidates to account for potential duplicates
            fetch_k = max(k * 3, 10)
            distances, indices = self.index.search(query_vector, fetch_k)

            results = []
            seen_texts = set()
            for i, idx in enumerate(indices[0]):
                if distances[0][i] <= 1.50 and idx < len(self.metadata) and idx >= 0:
                    item = self.metadata[idx]
                    if item['text'] not in seen_texts:
                        seen_texts.add(item['text'])
                        results.append(item)
                        if len(results) >= k:
                            break
            return results

    def format_context(self, results: List[Dict]) -> str:
        context_parts = []
        for res in results:
            context_parts.append(
                f"[{res['title']} ({res['year']})]: {res['text']}"
            )
        return "\n\n".join(context_parts)
