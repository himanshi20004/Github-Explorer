import faiss
import numpy as np
from embedder import embed_texts, embed_query, EMBED_DIM


def chunk_file(path: str, content: str, max_chars: int = 1500) -> list[dict]:
    """Split a file into overlapping chunks."""
    chunks = []
    lines = content.split("\n")
    current_chunk = []
    current_len = 0

    for line in lines:
        current_chunk.append(line)
        current_len += len(line) + 1

        if current_len >= max_chars:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "path": path,
                "content": chunk_text,
                "text": f"File: {path}\n\n{chunk_text}"
            })
            # overlap: keep last 10 lines
            current_chunk = current_chunk[-10:]
            current_len = sum(len(l) + 1 for l in current_chunk)

    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        if chunk_text.strip():
            chunks.append({
                "path": path,
                "content": chunk_text,
                "text": f"File: {path}\n\n{chunk_text}"
            })

    return chunks


class RepoVectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []

    def build(self, files: list[dict]):
        """Chunk all files, embed them, and build FAISS index."""
        self.chunks = []
        for f in files:
            self.chunks.extend(chunk_file(f["path"], f["content"]))

        print(f"[VectorStore] Created {len(self.chunks)} chunks")
        texts = [c["text"] for c in self.chunks]

        print("[VectorStore] Embedding chunks with Gemini...")
        embeddings = embed_texts(texts)

        self.index = faiss.IndexFlatIP(EMBED_DIM)  # Inner product (cosine after normalize)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        print(f"[VectorStore] FAISS index built with {self.index.ntotal} vectors")

    def search(self, query: str, k: int = 6) -> list[dict]:
        """Search for top-k relevant chunks."""
        q_emb = embed_query(query)
        faiss.normalize_L2(q_emb)
        distances, indices = self.index.search(q_emb, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append({**self.chunks[idx], "score": float(dist)})
        return results