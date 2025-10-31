"""
Complete retrieval pipeline combining vector search and reranking.
Implements Dependency Injection and Open/Closed Principle.
"""
import logging
from typing import List, Optional

from interfaces import (
    IRetrievalPipeline,
    IEmbeddingGenerator,
    IVectorDatabase,
    IReranker,
    SearchResult
)
from config import RetrievalConfig

logger = logging.getLogger(__name__)

class RetrievalPipeline(IRetrievalPipeline):
    """
    End-to-end retrieval pipeline.
    
    Architecture follows Dependency Injection:
    - Depends on abstractions (interfaces), not concrete implementations
    - Components can be swapped without changing pipeline code
    - Easy to test with mock implementations
    
    Two-stage retrieval:
    1. Fast vector search (get top 50)
    2. Precise reranking (refine to top 10)
    """
    
    def __init__(
        self,
        embedder: IEmbeddingGenerator,
        vector_db: IVectorDatabase,
        reranker: IReranker,
        config: RetrievalConfig
    ):
        """
        Initialize retrieval pipeline.
        
        Args:
            embedder: Embedding generator
            vector_db: Vector database
            reranker: Reranker
            config: Retrieval configuration
        """
        self.embedder = embedder
        self.vector_db = vector_db
        self.reranker = reranker
        self.config = config
        logger.info("RetrievalPipeline initialized")
    
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_reranking: bool = True
    ) -> List[SearchResult]:
        """
        Retrieve relevant documents for a query.
        
        Process:
        1. Generate query embedding (input_type="query")
        2. Vector search in Qdrant (fast, get many candidates)
        3. Rerank candidates (slow, refine to best matches)
        
        Args:
            query: Search query
            top_k: Number of final results (uses config default if None)
            use_reranking: Whether to apply reranking
            
        Returns:
            List of relevant documents, ranked by relevance
        """
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        final_top_k = top_k or self.config.rerank_top_k
        
        try:
            # Step 1: Generate query embedding
            logger.info(f"Generating embedding for query: '{query[:50]}...'")
            query_embedding = await self.embedder.generate_embedding(
                text=query,
                input_type="query"  # Important: use "query" type for search
            )
            
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []
            
            # Step 2: Vector search
            logger.info(f"Searching vector database (top_k={self.config.initial_top_k})...")
            initial_results = await self.vector_db.search(
                query_embedding=query_embedding,
                top_k=self.config.initial_top_k,
                score_threshold=self.config.score_threshold
            )
            
            if not initial_results:
                logger.info("No results found in vector search")
                return []
            
            logger.info(f"Vector search returned {len(initial_results)} results")
            
            # Step 3: Rerank (optional but recommended)
            if use_reranking and len(initial_results) > 0:
                logger.info(f"Reranking top {final_top_k} results...")
                final_results = await self.reranker.rerank(
                    query=query,
                    results=initial_results,
                    top_k=final_top_k
                )
            else:
                logger.info("Skipping reranking")
                final_results = initial_results[:final_top_k]
            
            logger.info(f"✓ Retrieved {len(final_results)} final results")
            return final_results
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    async def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_reranking: bool = True,
        include_context: bool = True
    ) -> dict:
        """
        Retrieve documents with additional context and metadata.
        
        Returns structured response suitable for RAG systems.
        
        Args:
            query: Search query
            top_k: Number of results
            use_reranking: Whether to apply reranking
            include_context: Include surrounding chunks for context
            
        Returns:
            Dictionary with results and metadata
        """
        results = await self.retrieve(query, top_k, use_reranking)
        
        response = {
            "query": query,
            "results_count": len(results),
            "results": [
                {
                    "content": result.content,
                    "score": result.score,
                    "source": result.source,
                    "page_number": result.page_number,
                    "metadata": result.metadata
                }
                for result in results
            ],
            "reranked": use_reranking
        }
        
        return response
