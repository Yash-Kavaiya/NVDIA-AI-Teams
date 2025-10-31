"""NVIDIA reranker using LangChain."""
import logging
from typing import List
from langchain_nvidia_ai_endpoints import NVIDIARerank
from langchain_core.documents import Document as LangChainDocument
from .interfaces import IReranker, Document, SearchResult

logger = logging.getLogger(__name__)

class NvidiaReranker(IReranker):
    """Rerank search results using NVIDIA AI endpoints."""
    
    def __init__(self, api_key: str, model: str = "nvidia/llama-3.2-nv-rerankqa-1b-v2"):
        """
        Initialize NVIDIA reranker.
        
        Args:
            api_key: NVIDIA API key
            model: NVIDIA reranker model name
        """
        self.api_key = api_key
        self.model = model
        
        # Initialize NVIDIA reranker client
        self.client = NVIDIARerank(
            model=model,
            api_key=api_key
        )
        
        logger.info(f"Initialized NvidiaReranker with model: {model}")
    
    def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[SearchResult]:
        """
        Rerank documents based on relevance to query.
        
        Args:
            query: Search query
            documents: List of Document objects to rerank
            top_n: Number of top results to return
            
        Returns:
            List of SearchResult objects sorted by relevance (descending)
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        if not documents:
            logger.warning("No documents to rerank")
            return []
        
        try:
            logger.info(f"Reranking {len(documents)} documents for query: {query[:100]}...")
            
            # Convert to LangChain documents format
            langchain_docs = [
                LangChainDocument(page_content=doc.content)
                for doc in documents
            ]
            
            # Rerank using NVIDIA API
            reranked = self.client.compress_documents(
                query=query,
                documents=langchain_docs
            )
            
            # Take top N results
            reranked = reranked[:top_n]
            
            # Convert back to SearchResult objects
            results = []
            for rank, lc_doc in enumerate(reranked):
                # Find original document
                original_doc = None
                for doc in documents:
                    if doc.content == lc_doc.page_content:
                        original_doc = doc
                        break
                
                if original_doc is None:
                    logger.warning(f"Could not find original document for reranked result {rank}")
                    continue
                
                # Create SearchResult with reranked score
                # Note: LangChain NVIDIARerank returns documents with relevance_score in metadata
                score = lc_doc.metadata.get('relevance_score', 1.0 / (rank + 1))
                
                result = SearchResult(
                    document=original_doc,
                    score=score,
                    rank=rank + 1
                )
                results.append(result)
            
            logger.info(f"Reranked to top {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise
    
    def rerank_with_scores(self, query: str, documents: List[Document], top_n: int = 5) -> List[dict]:
        """
        Rerank and return results with detailed scores.
        
        Args:
            query: Search query
            documents: List of Document objects to rerank
            top_n: Number of top results to return
            
        Returns:
            List of dicts with 'document', 'score', and 'rank' keys
        """
        results = self.rerank(query, documents, top_n)
        
        return [
            {
                "document": result.document,
                "score": result.score,
                "rank": result.rank,
                "content_preview": result.document.content[:200] + "..." if len(result.document.content) > 200 else result.document.content
            }
            for result in results
        ]
