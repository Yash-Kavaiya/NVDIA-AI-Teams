"""Qdrant database manager."""
import logging
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from config.config import QdrantConfig

logger = logging.getLogger(__name__)

class QdrantManager:
    """Manages Qdrant operations."""
    
    def __init__(self, config: QdrantConfig):
        """Initialize Qdrant manager."""
        self.config = config
        self.client = QdrantClient(url=config.url)
        logger.info(f"Connected to Qdrant at {config.url}")
    
    def create_collection_if_not_exists(self) -> None:
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
                logger.info(f"✓ Created collection '{self.config.collection_name}'")
            else:
                logger.info(f"✓ Collection '{self.config.collection_name}' already exists")
        except Exception as e:
            logger.error(f"✗ Error creating collection: {e}")
            raise
    
    def upsert_points(self, points: List[PointStruct]) -> bool:
        """Upload points to Qdrant."""
        try:
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=points
            )
            logger.debug(f"Uploaded {len(points)} points to Qdrant")
            return True
        except Exception as e:
            logger.error(f"Error upserting points: {e}")
            return False
    
    def get_collection_info(self) -> dict:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.config.collection_name)
            return {
                "name": self.config.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}