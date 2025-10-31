"""NVIDIA embedding generator using LangChain."""
import logging
from typing import List
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from .interfaces import IEmbeddingGenerator

logger = logging.getLogger(__name__)

class NvidiaEmbeddingGenerator(IEmbeddingGenerator):
    """Generate embeddings using NVIDIA AI endpoints."""
    
    def __init__(self, api_key: str, model: str = "nvidia/llama-3.2-nv-embedqa-1b-v2"):
        """
        Initialize NVIDIA embedding generator.
        
        Args:
            api_key: NVIDIA API key
            model: NVIDIA embedding model name
        """
        self.api_key = api_key
        self.model = model
        
        # Initialize NVIDIA embeddings client
        self.client = NVIDIAEmbeddings(
            model=model,
            api_key=api_key,
            truncate="NONE"
        )
        
        logger.info(f"Initialized NvidiaEmbeddingGenerator with model: {model}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts (documents/passages).
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # For documents, we embed them as passages
            # The model handles batch processing internally
            embeddings = self.client.embed_documents(texts)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query: Query string to embed
            
        Returns:
            Embedding vector
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        try:
            logger.info(f"Generating query embedding for: {query[:100]}...")
            
            # For queries, use embed_query which may have different preprocessing
            embedding = self.client.embed_query(query)
            
            logger.info("Generated query embedding")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise
    
    def embed_documents_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings in batches for large document sets.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process per batch
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            embeddings = self.generate_embeddings(batch)
            all_embeddings.extend(embeddings)
        
        return all_embeddings
