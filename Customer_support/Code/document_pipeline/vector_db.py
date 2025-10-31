"""
Qdrant vector database operations.
Implements Single Responsibility Principle - only handles vector database operations.
"""
import logging
from typing import List
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct, 
    VectorParams, 
    Distance,
    SearchRequest
)

from interfaces import IVectorDatabase, DocumentChunk, SearchResult
from config import QdrantConfig

logger = logging.getLogger(__name__)

class QdrantVectorDB(IVectorDatabase):
    """
    Manages Qdrant vector database operations.
    
    Qdrant is optimized for:
    - High-dimensional vectors (our 300-dim embeddings)
    - Cosine similarity search
    - Metadata filtering
    - Horizontal scaling
    """
    
    def __init__(self, config: QdrantConfig):
        """
        Initialize Qdrant client.
        
        Args:
            config: Qdrant configuration
        """
        self.config = config
        self.client = QdrantClient(url=config.url)
        logger.info(f"QdrantVectorDB connected to {config.url}")
    
    async def create_collection(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            if not self.client.collection_exists(self.config.collection_name):
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✓ Created collection: {self.config.collection_name}")
            else:
                logger.info(f"✓ Collection exists: {self.config.collection_name}")
        except Exception as e:
            logger.error(f"✗ Error creating collection: {e}")
            raise
    
    async def upsert_documents(
        self, 
        chunks: List[DocumentChunk], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        Insert or update document chunks with embeddings.
        
        Args:
            chunks: Document chunks
            embeddings: Corresponding embeddings
            
        Returns:
            True if successful
        """
        if len(chunks) != len(embeddings):
            logger.error("Mismatch between chunks and embeddings count")
            return False
        
        try:
            points = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is None:
                    logger.warning(f"Skipping chunk {i} - no embedding")
                    continue
                
                # Create unique ID based on source and chunk_id
                point_id = hash(f"{chunk.source}_{chunk.chunk_id}") & 0x7FFFFFFFFFFFFFFF
                
                # Prepare payload
                payload = {
                    "content": chunk.content,
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "page_number": chunk.page_number,
                    "metadata": chunk.metadata,
                    "processed_at": datetime.now().isoformat()
                }
                
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
            
            if not points:
                logger.warning("No valid points to upsert")
                return False
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            
            logger.info(f"✓ Upserted {len(points)} points to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error upserting documents: {e}")
            return False
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int, 
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        try:
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            search_results = []
            for result in results:
                search_result = SearchResult(
                    content=result.payload.get("content", ""),
                    score=result.score,
                    metadata=result.payload.get("metadata", {}),
                    source=result.payload.get("source", ""),
                    page_number=result.payload.get("page_number")
                )
                search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.config.collection_name)
            return {
                "name": self.config.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}
