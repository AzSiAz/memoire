import requests
import numpy as np
from typing import List, Union

OLLAMA_API_URL = "http://llm:11434/api/embed"

def compute_embedding(text: Union[str, List[str]], model: str = "nomic-embed-text") -> np.ndarray:
    """
    Compute embeddings for a text or list of texts using Ollama.
    """
    if isinstance(text, str):
        text = [text]
    
    response = requests.post(
        OLLAMA_API_URL,
        json={
            "model": model,
            "input": text,
            "truncate": False
        },
    )

    response.raise_for_status()
    embeddings = response.json()["embeddings"]

    return embeddings 
