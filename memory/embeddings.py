import requests
import numpy as np
from typing import List, Union

OLLAMA_API_URL = "http://llm:11434/api/embed"

def compute_embedding(text: Union[str, List[str]], model: str = "nomic-embed-text") -> np.ndarray:
    """
    Compute embeddings for a text or list of texts using Ollama.
    
    Args:
        text: A single text string or list of text strings to embed
        model: The Ollama model to use for embeddings (default: nomic-embed-text)
    
    Returns:
        A numpy array of shape (n, 768) where n is the number of input texts
    """
    if isinstance(text, str):
        text = [text]
    
    response = requests.post(
        OLLAMA_API_URL,
        json={
            "model": model,
            "input": text
        },
    )

    response.raise_for_status()
    embeddings = response.json()["embeddings"]

    return embeddings 
