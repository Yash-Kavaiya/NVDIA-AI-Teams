"""
Product Search Agent Tools for Fashion Image Retrieval

This module provides tools for semantic search across fashion products using
NVIDIA embeddings and Qdrant vector database.

Technical Stack:
- NVIDIA nv-embed-v1: Multimodal embeddings (4096-dim)
- Qdrant: Vector similarity search with metadata filtering
- Async operations: Concurrent processing for performance
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the image_embeddings_pipeline to Python path
PIPELINE_PATH = Path(__file__).parent.parent.parent.parent / "image_embeddings_pipeline"
sys.path.insert(0, str(PIPELINE_PATH))

from config.config import Config
from src.search_engine import ImageSearchEngine, SearchResult
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

logger = logging.getLogger(__name__)

# Global search engine instance
_search_engine: Optional[ImageSearchEngine] = None


def _get_search_engine() -> ImageSearchEngine:
    """
    Initialize and return the search engine instance.
    Uses lazy initialization to load config only when needed.
    """
    global _search_engine
    if _search_engine is None:
        try:
            config = Config.from_env()
            config.validate()
            _search_engine = ImageSearchEngine(config)
            logger.info("Product search engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {e}")
            raise RuntimeError(f"Search engine initialization failed: {e}")
    return _search_engine


def search_products_by_text(
    query: str, 
    limit: int = 10, 
    score_threshold: float = 0.0
) -> Dict[str, Any]:
    """
    Search for fashion products using natural language text descriptions.
    
    This function leverages NVIDIA's multimodal embeddings to understand the
    semantic meaning of your query and find visually matching products.
    
    Examples:
        - "red floral summer dress"
        - "black leather ankle boots"
        - "casual men's denim jacket"
        - "vintage gold watch"
    
    Args:
        query: Natural language description of the product you're looking for
        limit: Maximum number of results to return (default: 10, max: 50)
        score_threshold: Minimum similarity score (0.0-1.0). Higher = more strict.
                        Recommended: 0.7 for balanced results, 0.8 for high precision
    
    Returns:
        Dictionary containing:
            - query: The original search query
            - results_count: Number of results found
            - results: List of matching products with scores, URLs, and metadata
            - search_params: Parameters used for the search
    """
    try:
        # Validate inputs
        limit = max(1, min(limit, 50))  # Cap at 50 for performance
        score_threshold = max(0.0, min(score_threshold, 1.0))
        
        if not query or not query.strip():
            return {
                "error": "Query cannot be empty",
                "query": query,
                "results_count": 0,
                "results": []
            }
        
        # Get search engine
        engine = _get_search_engine()
        
        # Run async search in sync context
        results = asyncio.run(
            engine.search_by_text(query, limit=limit, score_threshold=score_threshold)
        )
        
        # Format results
        formatted_results = [
            {
                "id": result.id,
                "filename": result.filename,
                "image_url": result.image_url,
                "similarity_score": round(result.score, 4),
                "processed_at": result.processed_at
            }
            for result in results
        ]
        
        return {
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results,
            "search_params": {
                "limit": limit,
                "score_threshold": score_threshold,
                "search_type": "text_to_image"
            }
        }
        
    except Exception as e:
        logger.error(f"Text search error: {e}")
        return {
            "error": f"Search failed: {str(e)}",
            "query": query,
            "results_count": 0,
            "results": []
        }


def search_products_by_image(
    image_url: str,
    limit: int = 10,
    score_threshold: float = 0.0
) -> Dict[str, Any]:
    """
    Find visually similar products by providing an image URL.
    
    Perfect for:
        - Finding alternatives to out-of-stock items
        - Discovering similar styles
        - Visual product recommendations
        - Reverse image search
    
    Args:
        image_url: Public URL of the image to search with
        limit: Maximum number of similar products to return (default: 10, max: 50)
        score_threshold: Minimum similarity score (0.0-1.0)
    
    Returns:
        Dictionary containing similar products ranked by visual similarity
    """
    try:
        # Validate inputs
        limit = max(1, min(limit, 50))
        score_threshold = max(0.0, min(score_threshold, 1.0))
        
        if not image_url or not image_url.startswith('http'):
            return {
                "error": "Invalid image URL. Must start with http:// or https://",
                "image_url": image_url,
                "results_count": 0,
                "results": []
            }
        
        # Get search engine
        engine = _get_search_engine()
        
        # Run async search
        results = asyncio.run(
            engine.search_by_image(image_url, limit=limit, score_threshold=score_threshold)
        )
        
        # Format results
        formatted_results = [
            {
                "id": result.id,
                "filename": result.filename,
                "image_url": result.image_url,
                "similarity_score": round(result.score, 4),
                "processed_at": result.processed_at
            }
            for result in results
        ]
        
        return {
            "query_image": image_url,
            "results_count": len(formatted_results),
            "results": formatted_results,
            "search_params": {
                "limit": limit,
                "score_threshold": score_threshold,
                "search_type": "image_to_image"
            }
        }
        
    except Exception as e:
        logger.error(f"Image search error: {e}")
        return {
            "error": f"Image search failed: {str(e)}",
            "image_url": image_url,
            "results_count": 0,
            "results": []
        }


def search_with_filters(
    query: str,
    filename_pattern: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Advanced search combining semantic similarity with metadata filtering.
    
    This provides surgical precision by filtering results based on both
    semantic meaning AND structured metadata.
    
    Args:
        query: Text description of what you're looking for
        filename_pattern: Filter by filename (e.g., "shoes", "dress")
        date_from: Only show products indexed after this date (ISO format: YYYY-MM-DD)
        date_to: Only show products indexed before this date (ISO format: YYYY-MM-DD)
        limit: Maximum results (default: 10)
    
    Returns:
        Dictionary containing filtered search results
        
    Example:
        search_with_filters(
            query="red shoes",
            filename_pattern="nike",
            date_from="2024-01-01",
            limit=5
        )
    """
    try:
        # Validate inputs
        limit = max(1, min(limit, 50))
        
        if not query or not query.strip():
            return {
                "error": "Query cannot be empty",
                "results_count": 0,
                "results": []
            }
        
        # Get search engine
        engine = _get_search_engine()
        
        # Run async filtered search
        results = asyncio.run(
            engine.search_with_filters(
                query=query,
                filename_pattern=filename_pattern,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
        )
        
        # Format results
        formatted_results = [
            {
                "id": result.id,
                "filename": result.filename,
                "image_url": result.image_url,
                "similarity_score": round(result.score, 4),
                "processed_at": result.processed_at
            }
            for result in results
        ]
        
        return {
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results,
            "filters_applied": {
                "filename_pattern": filename_pattern,
                "date_from": date_from,
                "date_to": date_to
            },
            "search_params": {
                "limit": limit,
                "search_type": "filtered_text_search"
            }
        }
        
    except Exception as e:
        logger.error(f"Filtered search error: {e}")
        return {
            "error": f"Filtered search failed: {str(e)}",
            "query": query,
            "results_count": 0,
            "results": []
        }


def get_collection_stats() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the product collection.
    
    Returns information about:
        - Total number of indexed products
        - Collection health metrics
        - Vector count and indexing status
        - Database configuration
    
    Returns:
        Dictionary containing collection statistics
    """
    try:
        engine = _get_search_engine()
        stats = engine.get_collection_stats()
        
        return {
            "collection_name": stats.get("collection_name", "Unknown"),
            "total_products": stats.get("points_count", 0),
            "indexed_vectors": stats.get("indexed_vectors_count", 0),
            "collection_status": stats.get("status", "Unknown"),
            "health": {
                "all_vectors_indexed": stats.get("vectors_count", 0) == stats.get("indexed_vectors_count", 0),
                "vectors_count": stats.get("vectors_count", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        return {
            "error": f"Failed to retrieve collection stats: {str(e)}",
            "collection_name": "Unknown",
            "total_products": 0
        }


def get_product_by_id(product_id: int) -> Dict[str, Any]:
    """
    Retrieve a specific product by its unique ID.
    
    Useful for:
        - Getting full details of a product from search results
        - Verifying product information
        - Debugging or troubleshooting
    
    Args:
        product_id: The unique integer ID of the product
    
    Returns:
        Dictionary containing full product details including metadata
    """
    try:
        engine = _get_search_engine()
        config = Config.from_env()
        client = QdrantClient(url=config.qdrant.url)
        
        # Retrieve point from Qdrant
        point = client.retrieve(
            collection_name=config.qdrant.collection_name,
            ids=[product_id]
        )
        
        if not point or len(point) == 0:
            return {
                "error": f"Product with ID {product_id} not found",
                "product_id": product_id
            }
        
        product = point[0]
        
        return {
            "product_id": product.id,
            "filename": product.payload.get('filename', 'Unknown'),
            "image_url": product.payload.get('image_url', ''),
            "processed_at": product.payload.get('processed_at', 'Unknown'),
            "metadata": {
                k: v for k, v in product.payload.items() 
                if k not in ['filename', 'image_url', 'processed_at']
            }
        }
        
    except Exception as e:
        logger.error(f"Product retrieval error: {e}")
        return {
            "error": f"Failed to retrieve product: {str(e)}",
            "product_id": product_id
        }
