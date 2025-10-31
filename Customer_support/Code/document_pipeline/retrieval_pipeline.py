"""End-to-end retrieval pipeline."""
import logging
from typing import List
from .interfaces import IEmbeddingGenerator, IVectorDB, IReranker, SearchResult
from .config import RetrievalConfig

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    """Complete retrieval pipeline with embedding, search, and reranking."""
    
    def __init__(
        self,
        embedding_generator: IEmbeddingGenerator,
        vector_db: IVectorDB,
        reranker: IReranker,
        config: RetrievalConfig
    ):
        """
        Initialize retrieval pipeline.
        
        Args:
            embedding_generator: Embedding generator instance
            vector_db: Vector database instance
            reranker: Reranker instance
            config: Retrieval configuration
        """
        self.embedding_generator = embedding_generator
        self.vector_db = vector_db
        self.reranker = reranker
        self.config = config
        
        logger.info("Initialized RetrievalPipeline")
    
    def search(self, query: str) -> List[SearchResult]:
        """
        Perform complete search: embed query -> vector search -> rerank.
        
        Args:
            query: Search query string
            
        Returns:
            List of reranked SearchResult objects
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        try:
            logger.info(f"Searching for: {query[:100]}...")
            
            # Step 1: Generate query embedding
            logger.info("Generating query embedding...")
            query_embedding = self.embedding_generator.generate_query_embedding(query)
            
            # Step 2: Vector search
            logger.info(f"Performing vector search (top_k={self.config.top_k})...")
            initial_results = self.vector_db.search(
                query_embedding=query_embedding,
                top_k=self.config.top_k
            )
            
            if not initial_results:
                logger.warning("No results found in vector search")
                return []
            
            # Step 3: Filter by score threshold
            filtered_results = [
                result for result in initial_results
                if result.score >= self.config.score_threshold
            ]
            
            logger.info(f"Filtered to {len(filtered_results)} results above threshold {self.config.score_threshold}")
            
            if not filtered_results:
                logger.warning("No results above score threshold")
                return []
            
            # Step 4: Rerank
            logger.info(f"Reranking top {self.config.rerank_top_n} results...")
            documents = [result.document for result in filtered_results]
            reranked_results = self.reranker.rerank(
                query=query,
                documents=documents,
                top_n=self.config.rerank_top_n
            )
            
            logger.info(f"Search complete. Returning {len(reranked_results)} results")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_with_details(self, query: str) -> dict:
        """
        Perform search and return detailed results.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with query, results, and metadata
        """
        results = self.search(query)
        
        return {
            "query": query,
            "num_results": len(results),
            "results": [
                {
                    "rank": result.rank,
                    "score": result.score,
                    "content": result.document.content,
                    "metadata": result.document.metadata
                }
                for result in results
            ]
        }
    
    def batch_search(self, queries: List[str]) -> List[List[SearchResult]]:
        """
        Perform multiple searches.
        
        Args:
            queries: List of query strings
            
        Returns:
            List of result lists (one per query)
        """
        all_results = []
        
        for i, query in enumerate(queries):
            logger.info(f"Processing query {i+1}/{len(queries)}")
            results = self.search(query)
            all_results.append(results)
        
        return all_results
