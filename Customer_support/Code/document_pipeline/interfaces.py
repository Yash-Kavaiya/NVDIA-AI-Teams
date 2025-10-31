"""Interface definitions for document pipeline components."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Document:
    """Represents a document chunk with metadata."""
    content: str
    metadata: Dict[str, Any]
    embedding: List[float] = None
    
@dataclass
class SearchResult:
    """Represents a search result."""
    document: Document
    score: float
    rank: int

class IDocumentExtractor(ABC):
    """Interface for document extraction."""
    
    @abstractmethod
    def extract(self, file_path: str) -> str:
        """Extract text from a document file."""
        pass
    
class IChunker(ABC):
    """Interface for text chunking."""
    
    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """Split text into chunks with metadata."""
        pass

class IEmbeddingGenerator(ABC):
    """Interface for generating embeddings."""
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass
    
    @abstractmethod
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a search query."""
        pass

class IVectorDB(ABC):
    """Interface for vector database operations."""
    
    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a new collection."""
        pass
    
    @abstractmethod
    def upsert_documents(self, documents: List[Document]) -> None:
        """Insert or update documents in the database."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        pass

class IReranker(ABC):
    """Interface for reranking search results."""
    
    @abstractmethod
    def rerank(self, query: str, documents: List[Document], top_n: int) -> List[SearchResult]:
        """Rerank documents based on relevance to query."""
        pass
