import os
import json
import numpy as np
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
            # Simple keyword matching for demo
            query_terms = query.lower().split()
            scored_results = []
            for item in self.metadata:
                score = 0
                text_lower = item['text'].lower()
                for term in query_terms:
                    if term in text_lower:
                        score += 1
                if score > 0:
                    scored_results.append((score, item))
            
            # Sort by score descending
            scored_results.sort(key=lambda x: x[0], reverse=True)
            return [item for score, item in scored_results[:k]]
        else:
            query_vector = self.model.encode([query]).astype('float32')
            distances, indices = self.index.search(query_vector, k)
            
            results = []
            for idx in indices[0]:
                if idx < len(self.metadata) and idx >= 0:
                    results.append(self.metadata[idx])
            return results

    def format_context(self, results: List[Dict]) -> str:
        context_parts = []
        for res in results:
            context_parts.append(
                f"[{res['title']} ({res['year']})]: {res['text']}"
            )
        return "\n\n".join(context_parts)
