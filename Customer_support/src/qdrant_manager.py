"""Qdrant vector database management module."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from config.config import QdrantConfig

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant vector database operations.
    
    Single Responsibility: Handle all Qdrant database interactions.
    """
    
    def __init__(self, config: QdrantConfig):
        """Initialize Qdrant manager.
        
        Args:
            config: Qdrant configuration (Dependency Injection)
        """
        self.config = config
        self.client = QdrantClient(url=config.url)
        logger.info(f"QdrantManager initialized, connecting to {config.url}")
        
        # Ensure collection exists
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists, create if not."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.config.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.config.collection_name}")
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Collection created successfully")
            else:
                logger.info(f"Collection {self.config.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}", exc_info=True)
            raise
    
    def insert_chunks(
        self, 
        chunks: List[Dict[str, Any]]
    ) -> int:
        """Insert document chunks with embeddings into Qdrant.
        
        Args:
            chunks: List of chunks with embeddings and metadata
            
        Returns:
            Number of successfully inserted chunks
        """
        if not chunks:
            logger.warning("No chunks provided for insertion")
            return 0
        
        logger.info(f"Inserting {len(chunks)} chunks into Qdrant")
        
        points = []
        
        for i, chunk in enumerate(chunks):
            # Validate chunk has embedding
            if "embedding" not in chunk:
                logger.warning(f"Skipping chunk {i}: no embedding found")
                continue
            
            # Create point
            point = PointStruct(
                id=i,  # Simple sequential ID, or use hash for uniqueness
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk["chunk_index"],
                    "source_filename": chunk["source_filename"],
                    "source_filepath": chunk["source_filepath"],
                    "char_count": chunk["char_count"],
                    "metadata": chunk.get("metadata", {}),
                    "inserted_at": datetime.utcnow().isoformat()
                }
            )
            
            points.append(point)
        
        try:
            # Insert points in batches
            batch_size = 100
            successful = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                
                self.client.upsert(
                    collection_name=self.config.collection_name,
                    points=batch
                )
                
                successful += len(batch)
                logger.debug(f"Inserted batch: {successful}/{len(points)}")
            
            logger.info(f"Successfully inserted {successful} chunks")
            return successful
            
        except Exception as e:
            logger.error(f"Error inserting chunks: {e}", exc_info=True)
            return 0
    
    def search(
        self, 
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks in Qdrant.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            filter_conditions: Optional filter conditions
            
        Returns:
            List of search results with text, metadata, and scores
        """
        try:
            logger.info(f"Searching for top {top_k} results")
            
            # Build filter if provided
            query_filter = None
            if filter_conditions:
                query_filter = self._build_filter(filter_conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # Format results
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "chunk_id": result.payload.get("chunk_id", ""),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "source_filename": result.payload.get("source_filename", ""),
                    "source_filepath": result.payload.get("source_filepath", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "char_count": result.payload.get("char_count", 0)
                })
            
            logger.info(f"Found {len(formatted_results)} results")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
            return []
    
    def _build_filter(self, conditions: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from conditions dictionary.
        
        Args:
            conditions: Dictionary of field:value pairs
            
        Returns:
            Qdrant Filter object
        """
        must_conditions = []
        
        for field, value in conditions.items():
            must_conditions.append(
                FieldCondition(
                    key=field,
                    match=MatchValue(value=value)
                )
            )
        
        return Filter(must=must_conditions)
    
    def delete_collection(self):
        """Delete the entire collection (use with caution!)."""
        try:
            logger.warning(f"Deleting collection: {self.config.collection_name}")
            self.client.delete_collection(self.config.collection_name)
            logger.info("Collection deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}", exc_info=True)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            info = self.client.get_collection(self.config.collection_name)
            
            return {
                "name": self.config.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
                "optimizer_status": info.optimizer_status,
                "vector_size": self.config.embedding_dim
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}", exc_info=True)
            return {}
    
    def count_documents(self) -> int:
        """Count total documents in collection.
        
        Returns:
            Number of documents
        """
        try:
            info = self.client.get_collection(self.config.collection_name)
            return info.points_count or 0
        except Exception as e:
            logger.error(f"Error counting documents: {e}", exc_info=True)
            return 0
