"""Embedding generation module using NVIDIA NeMo Retriever API."""

import logging
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI

from config.config import NVIDIAConfig

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using NVIDIA's NeMo Retriever API.
    
    Single Responsibility: Generate embeddings for text using NVIDIA API.
    """
    
    def __init__(self, config: NVIDIAConfig):
        """Initialize embedding generator.
        
        Args:
            config: NVIDIA configuration (Dependency Injection)
        """
        self.config = config
        self.client = OpenAI(
            base_url=config.embedding_url.replace("/v1/embeddings", "/v1"),
            api_key=config.api_key
        )
        logger.info(f"EmbeddingGenerator initialized with model: {config.embedding_model}")
    
    def generate_embedding(
        self, 
        text: str,
        input_type: str = "passage"
    ) -> Optional[List[float]]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            input_type: Type of input - "query" or "passage" (default: "passage")
            
        Returns:
            Embedding vector as list of floats, or None if error
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.config.embedding_model,
                encoding_format="float",
                extra_body={"input_type": input_type, "truncate": "NONE"}
            )
            
            embedding = response.data[0].embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            return None
    
    def generate_embeddings_batch(
        self, 
        texts: List[str],
        input_type: str = "passage",
        batch_size: int = 10
    ) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            input_type: Type of input - "query" or "passage"
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        logger.info(
            f"Generating embeddings for {len(texts)} texts in {total_batches} batches"
        )
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.config.embedding_model,
                    encoding_format="float",
                    extra_body={"input_type": input_type, "truncate": "NONE"}
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"Successfully processed batch {batch_num}")
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(
                    f"Error processing batch {batch_num}: {e}",
                    exc_info=True
                )
                # Add None for each failed text in batch
                all_embeddings.extend([None] * len(batch))
        
        successful = sum(1 for e in all_embeddings if e is not None)
        logger.info(f"Generated {successful}/{len(texts)} embeddings successfully")
        
        return all_embeddings


class DocumentEmbedder:
    """High-level interface for embedding document chunks.
    
    Single Responsibility: Coordinate embedding generation for documents.
    """
    
    def __init__(
        self, 
        embedding_generator: EmbeddingGenerator,
        batch_size: int = 10
    ):
        """Initialize document embedder.
        
        Args:
            embedding_generator: EmbeddingGenerator instance (Dependency Injection)
            batch_size: Batch size for processing
        """
        self.embedding_generator = embedding_generator
        self.batch_size = batch_size
        logger.info(f"DocumentEmbedder initialized with batch_size={batch_size}")
    
    def embed_chunks(
        self, 
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for document chunks.
        
        Args:
            chunks: List of chunk dictionaries from ChunkProcessor
            
        Returns:
            List of chunks with embeddings added
        """
        if not chunks:
            logger.warning("No chunks provided for embedding")
            return []
        
        logger.info(f"Embedding {len(chunks)} chunks")
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate_embeddings_batch(
            texts=texts,
            input_type="passage",
            batch_size=self.batch_size
        )
        
        # Add embeddings to chunks
        embedded_chunks = []
        
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is None:
                logger.warning(
                    f"Skipping chunk {chunk['chunk_id']} due to embedding failure"
                )
                continue
            
            embedded_chunk = {
                **chunk,
                "embedding": embedding,
                "embedding_dim": len(embedding)
            }
            
            embedded_chunks.append(embedded_chunk)
        
        logger.info(
            f"Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks"
        )
        
        return embedded_chunks
    
    def embed_query(self, query: str) -> Optional[List[float]]:
        """Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector or None if error
        """
        logger.info("Generating query embedding")
        
        embedding = self.embedding_generator.generate_embedding(
            text=query,
            input_type="query"
        )
        
        if embedding is None:
            logger.error("Failed to generate query embedding")
        
        return embedding


class Reranker:
    """Reranks search results using NVIDIA's reranking API.
    
    Single Responsibility: Rerank retrieved documents for improved relevance.
    """
    
    def __init__(self, config: NVIDIAConfig):
        """Initialize reranker.
        
        Args:
            config: NVIDIA configuration (Dependency Injection)
        """
        self.config = config
        self.client = OpenAI(
            base_url=config.rerank_url.replace("/v1/ranking", "/v1"),
            api_key=config.api_key
        )
        logger.info(f"Reranker initialized with model: {config.rerank_model}")
    
    def rerank(
        self, 
        query: str,
        documents: List[str],
        top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on relevance to query.
        
        Args:
            query: Search query
            documents: List of document texts to rerank
            top_n: Number of top results to return (None = all)
            
        Returns:
            List of dictionaries with 'index' and 'score' keys, sorted by relevance
        """
        if not documents:
            logger.warning("No documents provided for reranking")
            return []
        
        try:
            logger.info(f"Reranking {len(documents)} documents")
            
            # Note: The actual API endpoint and format may vary
            # This is based on typical reranking API patterns
            response = self.client.post(
                "/ranking",
                json={
                    "model": self.config.rerank_model,
                    "query": {"text": query},
                    "passages": [{"text": doc} for doc in documents],
                    "truncate": "NONE"
                }
            )
            
            # Parse response (adjust based on actual API response format)
            rankings = response.json().get("rankings", [])
            
            # Sort by score (descending)
            rankings.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # Limit to top_n if specified
            if top_n is not None:
                rankings = rankings[:top_n]
            
            logger.info(f"Reranking complete, returning top {len(rankings)} results")
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error during reranking: {e}", exc_info=True)
            # Return documents in original order with neutral scores
            return [
                {"index": i, "score": 0.0} 
                for i in range(len(documents))
            ]
