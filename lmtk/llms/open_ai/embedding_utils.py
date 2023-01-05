"""
This is a port of a small subset of OpenAI's embedding utils. The goal is to
decrease the number of dependencies. Many of the dependencies in the original
are for creating plots.

https://github.com/openai/openai-python/blob/main/openai/embeddings_utils.py
"""

from typing import List
from tenacity import retry, stop_after_attempt, wait_random_exponential

import numpy as np
import openai

default_engine = 'text-embedding-ada-002'

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, engine=default_engine) -> List[float]:

    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    return openai.Embedding.create(input=[text], engine=engine)["data"][0]["embedding"]

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embeddings(
    list_of_text: List[str], engine=default_engine
) -> List[List[float]]:
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."

    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]

    data = openai.Embedding.create(input=list_of_text, engine=engine).data
    data = sorted(data, key=lambda x: x["index"])  # maintain the same order as input.
    return [d["embedding"] for d in data]

def cosine_similarity(a, b):
    """
    According to the OpenAI docs, embeddings are now already normalized, so
    I've removed the normalization step.
    """
    return np.dot(a, b)
    # return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def distances_from_embeddings(
    query_embedding: List[float],
    embeddings: List[List[float]],
) -> List[List]:
    """Return the distances between a query embedding and a list of embeddings."""
    return [
        cosine_similarity(query_embedding, embedding)
        for embedding in embeddings
    ]

def indices_of_nearest_neighbors_from_distances(distances) -> np.ndarray:
    """Return a list of indices of nearest neighbors from a list of distances."""
    return np.argsort(distances)
