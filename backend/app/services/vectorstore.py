"""
Vector store service for knowledge base.
Uses FAISS for local vector storage with HuggingFace embeddings.
"""
import logging
from typing import Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Lazy-loaded instances
_embedding = None
_vectorstore = None


def _get_embedding():
    """
    Get or create the embedding model.
    Uses HuggingFace sentence-transformers for local embeddings.
    """
    global _embedding
    if _embedding is None:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            _embedding = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            logger.info("Embedding model initialized")
        except ImportError:
            # Fallback: use fake embeddings for development
            logger.warning("HuggingFace not available, using fake embeddings")
            from langchain_community.embeddings import FakeEmbeddings
            _embedding = FakeEmbeddings(size=384)
    return _embedding


def get_vectorstore():
    """
    Get or create the FAISS vector store.
    
    Returns:
        FAISS vector store instance, or None if initialization fails.
    """
    global _vectorstore

    if _vectorstore is None:
        try:
            from langchain_community.vectorstores import FAISS
            embedding = _get_embedding()
            # Initialize with a placeholder to avoid empty index issues
            _vectorstore = FAISS.from_texts(
                texts=["Welcome to support. How can I help you today?"],
                embedding=embedding,
                metadatas=[{"source": "system"}]
            )
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Return None - callers should handle gracefully
            return None

    return _vectorstore
