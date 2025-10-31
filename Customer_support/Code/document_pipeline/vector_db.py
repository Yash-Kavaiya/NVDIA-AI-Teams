"""
Qdrant vector database operations.
Implements Single Responsibility Principle - only handles vector database operations.
"""
import logging
from typing import List
from datetime import datetime
import uuid
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
    - High-dimensional vectors (our 2048-dim embeddings)
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
                
                # Validate embedding
                if not isinstance(embedding, list):
                    logger.error(f"Invalid embedding at index {i}: expected list, got {type(embedding)}")
                    continue
                
                if len(embedding) != self.config.embedding_dim:
                    logger.error(f"Invalid embedding at index {i}: expected {self.config.embedding_dim} dimensions, got {len(embedding)}")
                    continue
                
                # Check if all elements are numeric
                if not all(isinstance(x, (int, float)) for x in embedding):
                    logger.error(f"Invalid embedding at index {i}: contains non-numeric values. First few elements: {embedding[:5]}")
                    continue
                
                # Create a unique UUID-based ID for each chunk
                # This avoids collisions and is compatible with Qdrant
                unique_string = f"{chunk.source}_{chunk.chunk_id}_{i}"
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
                
                # Prepare payload - ensure all values are JSON serializable
                payload = {
                    "content": str(chunk.content)[:10000],  # Limit content length
                    "source": str(chunk.source),
                    "chunk_id": int(chunk.chunk_id),
                    "page_number": int(chunk.page_number) if chunk.page_number is not None else None,
                    "metadata": self._sanitize_metadata(chunk.metadata),
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
            
            # Upsert to Qdrant in batches to avoid payload size limits
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.config.collection_name,
                    points=batch
                )
                logger.info(f"✓ Upserted batch {i//batch_size + 1}: {len(batch)} points")
            
            logger.info(f"✓ Successfully upserted {len(points)} total points to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error upserting documents: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _sanitize_metadata(self, metadata: dict) -> dict:
        """
        Sanitize metadata to ensure JSON serialization.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Sanitized metadata dictionary
        """
        sanitized = {}
        for key, value in metadata.items():
            # Convert to JSON-serializable types
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [str(v) for v in value]
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_metadata(value)
            else:
                sanitized[key] = str(value)
        return sanitized
    
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