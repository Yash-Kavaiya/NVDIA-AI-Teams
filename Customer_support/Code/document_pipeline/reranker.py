"""
NVIDIA Reranker for improving retrieval quality.
Implements Single Responsibility Principle - only handles reranking.
"""
import logging
import requests
from typing import List

from interfaces import IReranker, SearchResult
from config import NvidiaAPIConfig

logger = logging.getLogger(__name__)

class NvidiaReranker(IReranker):
    """
    Reranks search results using NVIDIA's NV-RerankQA model.
    
    Why reranking matters:
    - Vector search is fast but can miss nuanced relevance
    - Reranking uses cross-attention between query and documents
    - Significantly improves precision for top-k results
    - Trade-off: slower but more accurate
    """
    
    def __init__(self, config: NvidiaAPIConfig):
        """
        Initialize reranker.
        
        Args:
            config: NVIDIA API configuration
        """
        self.config = config
        self.rerank_url = "https://ai.api.nvidia.com/v1/retrieval/nvidia/llama-3_2-nv-rerankqa-1b-v2/reranking"
        self.session = requests.Session()
        logger.info("NvidiaReranker initialized")
    
    async def rerank(
        self, 
        query: str, 
        results: List[SearchResult], 
        top_k: int
    ) -> List[SearchResult]:
        """
        Rerank search results for better relevance.
        
        Process:
        1. Send query + all candidate passages to reranker
        2. Model computes relevance scores using cross-attention
        3. Sort by new scores
        4. Return top_k results
        
        Args:
            query: Original search query
            results: Initial search results from vector DB
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        if not results:
            logger.warning("No results to rerank")
            return []
        
        if len(results) <= top_k:
            logger.info(f"Results ({len(results)}) <= top_k ({top_k}), reranking all")
        
        try:
            # Prepare passages for reranking
            passages = []
            for result in results:
                passages.append({
                    "text": result.content
                })
            
            # Rerank API request
            payload = {
                "model": self.config.reranker_model,
                "query": {
                    "text": query
                },
                "passages": passages
            }
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                self.rerank_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            rerank_data = response.json()
            
            # Extract rankings
            if "rankings" not in rerank_data:
                logger.warning("No rankings in reranker response")
                return results[:top_k]
            
            rankings = rerank_data["rankings"]
            
            # Map reranked results back to original SearchResult objects
            reranked_results = []
            for ranking in rankings[:top_k]:
                index = ranking["index"]
                new_score = ranking.get("logit", results[index].score)
                
                # Update score with reranker score
                result = results[index]
                reranked_result = SearchResult(
                    content=result.content,
                    score=new_score,
                    metadata=result.metadata,
                    source=result.source,
                    page_number=result.page_number
                )
                reranked_results.append(reranked_result)
            
            logger.info(f"✓ Reranked {len(results)} → {len(reranked_results)} results")
            return reranked_results
            
        except requests.RequestException as e:
            logger.error(f"Reranking API error: {e}")
            # Fallback: return original results
            return results[:top_k]
        except Exception as e:
            logger.error(f"Reranking error: {e}")
            return results[:top_k]
    
    def __del__(self):
        """Close session on cleanup."""
        if hasattr(self, 'session'):
            self.session.close()
