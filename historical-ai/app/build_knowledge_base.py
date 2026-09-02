import os
import json
import re
from typing import List, Dict
import numpy as np

# Try importing ML libraries
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    ML_AVAILABLE = True
except ImportError:
    print("WARNING: ML libraries not found. Using Mock mode.")
    ML_AVAILABLE = False

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CHUNKS_DIR = os.path.join(BASE_DIR, "data", "chunks")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

METADATA_FILE = os.path.join(RAW_DIR, "metadata.json")
CHUNKS_FILE = os.path.join(CHUNKS_DIR, "chunks.json")
INDEX_FILE = os.path.join(VECTOR_DB_DIR, "index.faiss")
CHUNKS_META_FILE = os.path.join(VECTOR_DB_DIR, "chunks_metadata.json")

def load_metadata():
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text: str) -> str:
    # Remove OCR artifacts (simple placeholders)
    # Fix hyphenation at line ends
    text = re.sub(r'-\n', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text: str, metadata: Dict, chunk_size=120, overlap=30) -> List[Dict]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_content = " ".join(chunk_words)

        if len(chunk_words) < 20: # Skip very small chunks
            continue

        chunks.append({
            "text": chunk_content,
            "title": metadata["title"],
            "author": metadata["author"],
            "year": metadata["year"],
            "domain": metadata["domain"],
            "source_file": metadata["filename"]
        })
    return chunks

def build_knowledge_base():
    print("Step 1: Processing Data...")
    if not os.path.exists(CHUNKS_DIR):
        os.makedirs(CHUNKS_DIR)
    if not os.path.exists(VECTOR_DB_DIR):
        os.makedirs(VECTOR_DB_DIR)

    metadata_list = load_metadata()
    all_chunks = []

    for meta in metadata_list:
        file_path = os.path.join(RAW_DIR, meta["filename"])
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found.")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)
        file_chunks = chunk_text(cleaned_text, meta)
        all_chunks.extend(file_chunks)
        print(f"Processed {meta['filename']}: {len(file_chunks)} chunks.")

    # Save chunks
    with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Saved {len(all_chunks)} chunks to {CHUNKS_FILE}")

    # Step 2: Embeddings
    print("Step 2: Generating Embeddings...")

    if ML_AVAILABLE:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        texts = [f"Title: {c['title']}. Author: {c['author']}. Year: {c['year']}. Text: {c['text']}" for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Step 3: FAISS Index
        print("Step 3: Building Vector Index...")
        dimension = embeddings.shape[1]
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        faiss.write_index(index, INDEX_FILE)
    else:
        print("Skipping real embeddings (Mock Mode). Creating dummy index placeholder.")
        # Create a dummy file so retriever knows we are in mock mode or just to exist
        with open(os.path.join(VECTOR_DB_DIR, "mock_mode.flag"), 'w') as f:
            f.write("true")

    # Save metadata for retrieval mapping (index ID -> Metadata)
    with open(CHUNKS_META_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Knowledge Base Build Complete (ML Available: {ML_AVAILABLE}).")


if __name__ == "__main__":
    build_knowledge_base()
