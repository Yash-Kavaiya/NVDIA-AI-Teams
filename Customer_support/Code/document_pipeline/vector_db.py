"""Qdrant vector database implementation."""
import logging
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from .interfaces import IVectorDB, Document, SearchResult

logger = logging.getLogger(__name__)

class QdrantVectorDB(IVectorDB):
    """Qdrant vector database for document storage and retrieval."""
    
    def __init__(self, url: str, collection_name: str, vector_size: int):
        """
        Initialize Qdrant client.
        
        Args:
            url: Qdrant server URL
            collection_name: Name of the collection
            vector_size: Dimension of embedding vectors
        """
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        logger.info(f"Initialized QdrantVectorDB (collection={collection_name}, dim={vector_size})")
    
    def create_collection(self, collection_name: str = None, vector_size: int = None) -> None:
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name: Collection name (uses default if None)
            vector_size: Vector dimension (uses default if None)
        """
        coll_name = collection_name or self.collection_name
        vec_size = vector_size or self.vector_size
        
        try:
            # Check if collection exists
            if self.collection_exists(coll_name):
                logger.info(f"Collection '{coll_name}' already exists")
                return
            
            # Create collection with cosine distance
            self.client.create_collection(
                collection_name=coll_name,
                vectors_config=VectorParams(
                    size=vec_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created collection '{coll_name}' with dimension {vec_size}")
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def collection_exists(self, collection_name: str = None) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Collection name (uses default if None)
            
        Returns:
            True if collection exists, False otherwise
        """
        coll_name = collection_name or self.collection_name
        
        try:
            collections = self.client.get_collections().collections
            return any(c.name == coll_name for c in collections)
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False
    
    def upsert_documents(self, documents: List[Document]) -> None:
        """
        Insert or update documents in the database.
        
        Args:
            documents: List of Document objects with embeddings
        """
        if not documents:
            logger.warning("No documents to upsert")
            return
        
        # Validate embeddings
        for doc in documents:
            if doc.embedding is None:
                raise ValueError("Document must have embedding before upserting")
        
        try:
            # Create points for Qdrant
            points = []
            for i, doc in enumerate(documents):
                point = PointStruct(
                    id=i,  # Auto-increment ID
                    vector=doc.embedding,
                    payload={
                        "content": doc.content,
                        "metadata": doc.metadata
                    }
                )
                points.append(point)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
            logger.info(f"Upserted {len(documents)} documents to '{self.collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = 20) -> List[SearchResult]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects sorted by score (descending)
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")
        
        try:
            logger.info(f"Searching for top {top_k} similar documents")
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Convert to SearchResult objects
            results = []
            for rank, result in enumerate(search_results):
                doc = Document(
                    content=result.payload["content"],
                    metadata=result.payload["metadata"],
                    embedding=None  # Don't return embeddings in search results
                )
                
                search_result = SearchResult(
                    document=doc,
                    score=result.score,
                    rank=rank + 1
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def delete_collection(self, collection_name: str = None) -> None:
        """Delete a collection."""
        coll_name = collection_name or self.collection_name
        
        try:
            self.client.delete_collection(coll_name)
            logger.info(f"Deleted collection '{coll_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise
