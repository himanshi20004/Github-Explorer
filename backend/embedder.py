import os
import time
import cohere
import numpy as np

client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

EMBED_MODEL = "embed-english-v3.0"
EMBED_DIM = 1024


def embed_texts(texts: list[str], task_type=None) -> np.ndarray:
    all_embeddings = []
    batch_size = 90

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embed(
                texts=batch,
                model=EMBED_MODEL,
                input_type="search_document",
                embedding_types=["float"],
            )
            all_embeddings.extend(response.embeddings.float_)
            time.sleep(0.3)
        except Exception as e:
            print(f"[Embedder] Error: {e}")
            all_embeddings.extend([[0.0] * EMBED_DIM] * len(batch))

    return np.array(all_embeddings, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    response = client.embed(
        texts=[query],
        model=EMBED_MODEL,
        input_type="search_query",
        embedding_types=["float"],
    )
    return np.array(response.embeddings.float_[0], dtype="float32").reshape(1, -1)