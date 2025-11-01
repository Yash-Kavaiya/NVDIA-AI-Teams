"""
Customer Support Agent Tools

Provides tools for searching retail policy documents using NVIDIA RAG pipeline.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add customer_support directory to path
customer_support_path = Path(__file__).parent.parent.parent.parent / "customer_support"
sys.path.insert(0, str(customer_support_path))

from config.config import Config
from src.retrieval import RetrievalPipeline
from src.qdrant_manager import QdrantManager

logger = logging.getLogger(__name__)


class CustomerSupportTools:
    """Tools for customer support agent."""
    
    def __init__(self):
        """Initialize customer support tools with config."""
        try:
            self.config = Config.from_env()
            self.retrieval_pipeline = RetrievalPipeline(self.config)
            self.qdrant_manager = QdrantManager(self.config.qdrant)
            logger.info("CustomerSupportTools initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CustomerSupportTools: {e}")
            raise
    
    async def search_policy_documents(
        self,
        query: str,
        top_k: int = 5,
        use_reranking: bool = True,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Search retail policy documents for relevant information.
        
        This tool performs semantic search across indexed policy documents using
        NVIDIA embeddings and Qdrant vector database, with optional neural reranking.
        
        Args:
            query: The customer's question or search query
            top_k: Number of top results to return (default: 5)
            use_reranking: Whether to apply neural reranking (default: True)
            score_threshold: Minimum similarity score threshold (0-1, optional)
        
        Returns:
            Dictionary containing:
            - success: Whether the search succeeded
            - query: The original query
            - results_count: Number of results found
            - results: List of relevant document chunks with metadata
            - error: Error message if search failed
        
        Example:
            result = await search_policy_documents(
                query="What is the return policy for electronics?",
                top_k=5,
                use_reranking=True
            )
        """
        try:
            logger.info(f"Searching policy documents for: {query}")
            
            # Perform retrieval
            results = await self.retrieval_pipeline.search(
                query=query,
                top_k=top_k,
                rerank=use_reranking,
                score_threshold=score_threshold
            )
            
            if not results:
                logger.warning(f"No results found for query: {query}")
                return {
                    "success": True,
                    "query": query,
                    "results_count": 0,
                    "results": [],
                    "message": "No relevant policy documents found for this query. Try rephrasing or using different keywords."
                }
            
            # Format results for agent consumption
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = {
                    "rank": i,
                    "text": result["text"],
                    "source_filename": result["source_filename"],
                    "source_filepath": result.get("source_filepath", ""),
                    "chunk_id": result["chunk_id"],
                    "chunk_index": result["chunk_index"],
                    "similarity_score": result.get("score", 0.0),
                    "rerank_score": result.get("rerank_score", None),
                    "char_count": result.get("char_count", 0),
                    "metadata": result.get("metadata", {})
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            
            return {
                "success": True,
                "query": query,
                "results_count": len(formatted_results),
                "results": formatted_results,
                "reranking_applied": use_reranking,
                "message": f"Found {len(formatted_results)} relevant policy document(s)"
            }
            
        except Exception as e:
            logger.error(f"Error searching policy documents: {e}", exc_info=True)
            return {
                "success": False,
                "query": query,
                "results_count": 0,
                "results": [],
                "error": str(e),
                "message": "An error occurred while searching policy documents. Please try again."
            }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the policy document collection.
        
        Returns collection statistics including total number of indexed documents,
        collection status, and database health metrics.
        
        Returns:
            Dictionary containing:
            - success: Whether the operation succeeded
            - collection_name: Name of the collection
            - total_chunks: Total number of document chunks
            - status: Collection status
            - vector_size: Embedding dimension
            - error: Error message if operation failed
        
        Example:
            info = get_collection_info()
            print(f"Total indexed chunks: {info['total_chunks']}")
        """
        try:
            logger.info("Retrieving collection information")
            
            info = self.qdrant_manager.get_collection_info()
            
            if not info:
                return {
                    "success": False,
                    "error": "Unable to retrieve collection information",
                    "message": "Could not connect to policy document database"
                }
            
            return {
                "success": True,
                "collection_name": info.get("name", ""),
                "total_chunks": info.get("points_count", 0),
                "vectors_count": info.get("vectors_count", 0),
                "status": info.get("status", "unknown"),
                "vector_size": info.get("vector_size", 0),
                "optimizer_status": info.get("optimizer_status", "unknown"),
                "message": f"Collection contains {info.get('points_count', 0)} indexed document chunks"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred while retrieving collection information"
            }
    
    async def close(self):
        """Close resources."""
        try:
            await self.retrieval_pipeline.close()
            logger.info("CustomerSupportTools resources closed")
        except Exception as e:
            logger.error(f"Error closing resources: {e}")


# Create global instance
_tools_instance = None

def get_tools_instance() -> CustomerSupportTools:
    """Get or create the global tools instance."""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = CustomerSupportTools()
    return _tools_instance


# Tool functions for ADK agent
def search_policy_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Search retail policy documents for relevant information.
    
    Args:
        query: The customer's question or search query (REQUIRED)
        top_k: Number of top results to return (default: 5)
    
    Returns:
        Dictionary with search results including relevant policy excerpts,
        similarity scores, source documents, and metadata.
    """
    tools = get_tools_instance()
    
    # Run async function in event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        tools.search_policy_documents(query=query, top_k=top_k)
    )


def get_collection_info() -> Dict[str, Any]:
    """
    Get information about the policy document collection.
    
    Returns collection statistics including total number of indexed documents,
    collection status, and database health metrics.
    
    Returns:
        Dictionary with collection statistics and status information.
    """
    tools = get_tools_instance()
    return tools.get_collection_info()
