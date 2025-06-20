# utils/embeddings.py
from backend.config import main as config
from typing import List
import numpy as np

# Example with LangChain's Google Generative AI embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Initialize the embedding model (adjust this based on your provider)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key= config.GEMINI_API_KEY
)


def get_text_embedding(text: str) -> List[float]:
    """
    Generates an embedding for a single piece of text.
    """
    return embedding_model.embed_query(text)


def get_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of texts.
    """
    return embedding_model.embed_documents(texts)
