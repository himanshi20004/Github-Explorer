import os
import time
import numpy as np
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072


def embed_texts(texts: list[str], task_type="RETRIEVAL_DOCUMENT") -> np.ndarray:
    all_embeddings = []

    for text in texts:
        for attempt in range(3):
            try:
                result = client.models.embed_content(
                    model=EMBED_MODEL,
                    contents=text,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=EMBED_DIM,
                    ),
                )
                all_embeddings.append(result.embeddings[0].values)
                time.sleep(1.5)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait = (attempt + 1) * 10
                    print(f"[Embedder] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"[Embedder] Error: {e}")
                    all_embeddings.append([0.0] * EMBED_DIM)
                    break
        else:
            all_embeddings.append([0.0] * EMBED_DIM)

    return np.array(all_embeddings, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBED_DIM,
        ),
    )
    return np.array(result.embeddings[0].values, dtype="float32").reshape(1, -1)