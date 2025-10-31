"""
NVIDIA embedding generation with proper input types.
Implements Single Responsibility Principle - only handles embedding generation.
"""
import logging
from typing import List, Optional
from openai import OpenAI

from interfaces import IEmbeddingGenerator
from config import NvidiaAPIConfig

logger = logging.getLogger(__name__)

class NvidiaEmbeddingGenerator(IEmbeddingGenerator):
    """
    Generates embeddings using NVIDIA's NeMo Retriever model.
    
    Key differences from generic embeddings:
    - input_type="query" for search queries (optimized for retrieval)
    - input_type="passage" for documents (optimized for indexing)
    - 300-dimensional vectors (efficient yet powerful)
    - 2048 token limit
    """
    
    def __init__(self, config: NvidiaAPIConfig):
        """
        Initialize embedding generator.
        
        Args:
            config: NVIDIA API configuration
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        logger.info(f"NvidiaEmbeddingGenerator initialized with model: {config.embedding_model}")
    
    async def generate_embedding(
        self, 
        text: str, 
        input_type: str = "passage"
    ) -> Optional[List[float]]:
        """
        Generate single embedding.
        
        Args:
            text: Text to embed
            input_type: "query" or "passage"
            
        Returns:
            Embedding vector or None on failure
        """
        if not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.config.embedding_model,
                encoding_format="float",
                extra_body={
                    "input_type": input_type,
                    "truncate": "NONE"  # Fail if text exceeds limit
                }
            )
            
            if response.data and len(response.data) > 0:
                embedding = response.data[0].embedding
                # Log embedding structure for debugging
                if embedding:
                    logger.debug(f"Embedding type: {type(embedding)}, length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
                return embedding
            
            logger.warning("No embedding in API response")
            return None
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        input_type: str = "passage"
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Note: Current implementation processes sequentially for reliability.
        For production, implement proper batching with rate limiting.
        
        Args:
            texts: List of texts to embed
            input_type: "query" or "passage"
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            if not text.strip():
                logger.warning(f"Empty text at index {i}")
                embeddings.append(None)
                continue
            
            embedding = await self.generate_embedding(text, input_type)
            embeddings.append(embedding)
            
            # Log progress for large batches
            if (i + 1) % 10 == 0:
                logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
        
        success_count = sum(1 for e in embeddings if e is not None)
        logger.info(f"Batch complete: {success_count}/{len(texts)} successful")
        
        return embeddings
    
    def validate_text_length(self, text: str, max_tokens: int = 2048) -> bool:
        """
        Validate text doesn't exceed token limit.
        
        Args:
            text: Text to validate
            max_tokens: Maximum allowed tokens
            
        Returns:
            True if text is within limit
        """
        # Rough estimate: 1 token ≈ 0.75 words
        estimated_tokens = len(text.split()) * 0.75
        
        if estimated_tokens > max_tokens:
            logger.warning(f"Text exceeds token limit: {estimated_tokens:.0f} > {max_tokens}")
            return False
        
        return True
