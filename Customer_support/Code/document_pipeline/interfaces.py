"""
Abstract base classes (interfaces) for document processing components.
Following Interface Segregation Principle (ISP) - clients should not depend on interfaces they don't use.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Document:
    """Data class representing a document."""
    content: str
    metadata: Dict[str, Any]
    source: str
    page_number: Optional[int] = None

@dataclass
class DocumentChunk:
    """Data class representing a document chunk."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: int
    source: str
    page_number: Optional[int] = None

@dataclass
class SearchResult:
    """Data class representing a search result."""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str
    page_number: Optional[int] = None

class IDocumentExtractor(ABC):
    """Interface for document extraction."""
    
    @abstractmethod
    async def extract(self, file_path: str) -> List[Document]:
        """
        Extract text and metadata from a document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        pass

class ITextChunker(ABC):
    """Interface for text chunking."""
    
    @abstractmethod
    def chunk(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into smaller chunks.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        pass

class IEmbeddingGenerator(ABC):
    """Interface for embedding generation."""
    
    @abstractmethod
    async def generate_embedding(
        self, 
        text: str, 
        input_type: str = "passage"
    ) -> Optional[List[float]]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            input_type: "query" or "passage"
            
        Returns:
            Embedding vector or None on failure
        """
        pass
    
    @abstractmethod
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        input_type: str = "passage"
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            input_type: "query" or "passage"
            
        Returns:
            List of embedding vectors
        """
        pass

class IVectorDatabase(ABC):
    """Interface for vector database operations."""
    
    @abstractmethod
    async def create_collection(self) -> None:
        """Create collection if it doesn't exist."""
        pass
    
    @abstractmethod
    async def upsert_documents(
        self, 
        chunks: List[DocumentChunk], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        Insert or update documents with their embeddings.
        
        Args:
            chunks: Document chunks
            embeddings: Corresponding embeddings
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int, 
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        pass

class IReranker(ABC):
    """Interface for reranking search results."""
    
    @abstractmethod
    async def rerank(
        self, 
        query: str, 
        results: List[SearchResult], 
        top_k: int
    ) -> List[SearchResult]:
        """
        Rerank search results for better relevance.
        
        Args:
            query: Original query text
            results: Initial search results
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        pass

class IDocumentProcessor(ABC):
    """Interface for end-to-end document processing."""
    
    @abstractmethod
    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process all documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Processing statistics
        """
        pass

class IRetrievalPipeline(ABC):
    """Interface for retrieval pipeline."""
    
    @abstractmethod
    async def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        use_reranking: bool = True
    ) -> List[SearchResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results (uses config default if None)
            use_reranking: Whether to apply reranking
            
        Returns:
            List of relevant documents
        """
        pass
