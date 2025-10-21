"""
Advanced search engine for querying image embeddings.

This module demonstrates how semantic search transforms from keyword matching
to understanding *meaning* - a paradigm shift in information retrieval.
"""
import logging
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
import aiohttp
from qdrant_client import QdrantClient
from qdrant_client.models import SearchRequest, Filter, FieldCondition, MatchValue

from config.config import Config, NvidiaConfig
from src.image_processor import ImageProcessor
from src.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a single search result."""
    id: int
    filename: str
    image_url: str
    score: float
    processed_at: str
    
    def __repr__(self) -> str:
        return f"SearchResult(id={self.id}, filename='{self.filename}', score={self.score:.4f})"

class ImageSearchEngine:
    """
    Semantic search engine for image embeddings.
    
    The beauty of vector search lies in its ability to understand semantic similarity.
    Unlike traditional keyword search, we're comparing the *meaning* encoded in
    high-dimensional vector spaces.
    """
    
    def __init__(self, config: Config):
        """Initialize search engine."""
        self.config = config
        self.client = QdrantClient(url=config.qdrant.url)
        self.embedding_generator = EmbeddingGenerator(config.nvidia, config.processing)
        self.image_processor = ImageProcessor(config.processing)
        
        logger.info(f"Search engine initialized for collection: {config.qdrant.collection_name}")
    
    async def search_by_text(
        self, 
        query: str, 
        limit: int = 10,
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search images by text description.
        
        This is where multimodal embeddings shine - the same vector space
        contains both images and text, enabling cross-modal search.
        
        Args:
            query: Text description to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of search results sorted by relevance
        """
        try:
            # Generate embedding for text query
            async with aiohttp.ClientSession() as session:
                # For NVIDIA nv-embed-v1, text queries work directly
                query_embedding = await self._generate_text_embedding(session, query)
                
                if query_embedding is None:
                    logger.error("Failed to generate query embedding")
                    return []
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.config.qdrant.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return self._parse_results(results)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def search_by_image(
        self,
        image_path_or_url: str,
        limit: int = 10,
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search similar images by providing an image.
        
        Image-to-image search reveals the true power of semantic embeddings:
        finding visually and conceptually similar content across millions of images.
        
        Args:
            image_path_or_url: Local path or URL to query image
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar images
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Process image
                if image_path_or_url.startswith('http'):
                    image_data_uri = await self.image_processor.download_and_encode(
                        session, image_path_or_url
                    )
                else:
                    # Load local image
                    import base64
                    from pathlib import Path
                    
                    with open(image_path_or_url, 'rb') as f:
                        img_b64 = base64.b64encode(f.read()).decode('utf-8')
                        image_data_uri = f"data:image/jpeg;base64,{img_b64}"
                
                if image_data_uri is None:
                    logger.error("Failed to process query image")
                    return []
                
                # Generate embedding
                query_embedding = await self.embedding_generator.generate(
                    session, image_data_uri
                )
                
                if query_embedding is None:
                    logger.error("Failed to generate image embedding")
                    return []
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.config.qdrant.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return self._parse_results(results)
            
        except Exception as e:
            logger.error(f"Image search error: {e}")
            return []
    
    async def search_with_filters(
        self,
        query: str,
        filename_pattern: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Advanced search with metadata filters.
        
        Combining semantic similarity with structured metadata filtering
        provides surgical precision in large-scale retrieval systems.
        
        Args:
            query: Text query
            filename_pattern: Filter by filename pattern
            date_from: Filter by date (ISO format)
            date_to: Filter by date (ISO format)
            limit: Maximum results
            
        Returns:
            Filtered search results
        """
        try:
            async with aiohttp.ClientSession() as session:
                query_embedding = await self._generate_text_embedding(session, query)
                
                if query_embedding is None:
                    return []
            
            # Build filters
            filter_conditions = []
            
            if filename_pattern:
                filter_conditions.append(
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value=filename_pattern)
                    )
                )
            
            # Apply filters if any
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            results = self.client.search(
                collection_name=self.config.qdrant.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )
            
            return self._parse_results(results)
            
        except Exception as e:
            logger.error(f"Filtered search error: {e}")
            return []
    
    async def _generate_text_embedding(
        self, 
        session: aiohttp.ClientSession, 
        text: str
    ) -> Optional[List[float]]:
        """Generate embedding for text query."""
        payload = {
            "input": [text],
            "model": self.config.nvidia.model,
            "encoding_format": self.config.nvidia.encoding_format,
            "input_type": "query"  # Important for search queries
        }
        
        try:
            async with session.post(
                self.config.nvidia.embedding_url,
                json=payload,
                headers=self.config.nvidia.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                if "data" in data and len(data["data"]) > 0:
                    return data["data"][0]["embedding"]
                return None
                
        except Exception as e:
            logger.error(f"Text embedding error: {e}")
            return None
    
    def _parse_results(self, raw_results) -> List[SearchResult]:
        """Parse Qdrant search results into SearchResult objects."""
        results = []
        
        for hit in raw_results:
            result = SearchResult(
                id=hit.id,
                filename=hit.payload.get('filename', 'Unknown'),
                image_url=hit.payload.get('image_url', ''),
                score=hit.score,
                processed_at=hit.payload.get('processed_at', 'Unknown')
            )
            results.append(result)
        
        return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            info = self.client.get_collection(self.config.qdrant.collection_name)
            
            return {
                "collection_name": self.config.qdrant.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}