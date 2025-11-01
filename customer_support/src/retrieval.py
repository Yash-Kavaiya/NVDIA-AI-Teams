"""Retrieval module for customer support documents."""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import aiohttp
import numpy as np

from .embedding import EmbeddingGenerator
from .qdrant_manager import QdrantManager
from config.config import Config

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    """Handles document retrieval and reranking using NVIDIA models."""
    
    def __init__(self, config: Config):
        """Initialize retrieval pipeline.
        
        Args:
            config: Main configuration object
        """
        self.config = config
        self.embedding_generator = EmbeddingGenerator(config.nvidia)
        self.qdrant_manager = QdrantManager(config.qdrant)
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _rerank(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank passages using NVIDIA reranking model.
        
        Args:
            query: Search query
            passages: List of passages with text and metadata
            top_k: Number of results to return after reranking
            
        Returns:
            Reranked passages with scores
        """
        session = await self._get_session()
        
        # Prepare reranking payload
        payload = {
            "query": query,
            "passages": [p["text"] for p in passages],
            "truncate": "NONE"
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.nvidia.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create request
            response = await session.post(
                self.config.nvidia.rerank_url,
                json=payload,
                headers=headers,
                timeout=self.config.nvidia.request_timeout
            )
            if response.status != 200:
                logger.error(f"Reranking failed: {response.status}")
                return passages[:top_k]
                
            data = await response.json()
            scores = data["scores"]
            
            # Create copies of passages with rerank scores
            reranked = []
            for passage, score in zip(passages, scores):
                reranked_passage = passage.copy()
                reranked_passage["rerank_score"] = score
                reranked.append(reranked_passage)
            
            # Sort by rerank score and take top_k
            reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
            return reranked[:top_k]
                
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return passages[:top_k]

    async def search(
        self,
        query: str,
        top_k: int = 5,
        rerank: bool = True,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant passages.
        
        Args:
            query: Search query
            top_k: Number of results to return
            rerank: Whether to rerank results
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of relevant passages with scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Vector search
            vector_results = self.qdrant_manager.search(
                query_vector=query_embedding,
                top_k=top_k * 2 if rerank else top_k,  # Get more results if reranking
                score_threshold=score_threshold
            )
            
            if not vector_results:
                return []
                
            # Rerank if enabled
            if rerank:
                reranked_results = await self._rerank(
                    query=query,
                    passages=vector_results,
                    top_k=top_k
                )
                return reranked_results
            
            return vector_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def close(self):
        """Close resources."""
        if self.session:
            await self.session.close()
            self.session = None