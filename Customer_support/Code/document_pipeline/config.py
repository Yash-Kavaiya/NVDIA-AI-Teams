"""
Configuration management for document processing pipeline.
Following SOLID principles with dependency injection and single responsibility.
"""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class NvidiaAPIConfig:
    """NVIDIA API configuration for embeddings and reranking."""
    api_key: str
    base_url: str = "https://integrate.api.nvidia.com/v1"
    embedding_model: str = "nvidia/llama-3.2-nemoretriever-300m-embed-v2"
    reranker_model: str = "nvidia/llama-3.2-nv-rerankqa-1b-v2"
    ocr_url: str = "https://ai.api.nvidia.com/v1/cv/nvidia/nemoretriever-ocr-v1"
    
    @property
    def headers(self) -> dict:
        """Get API headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def validate(self) -> None:
        """Validate API configuration."""
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY is required")
        if not self.api_key.startswith("nvapi-"):
            raise ValueError("NVIDIA_API_KEY should start with 'nvapi-'")

@dataclass
class QdrantConfig:
    """Qdrant vector database configuration."""
    url: str
    collection_name: str
    embedding_dim: int = 300  # llama-3.2-nemoretriever-300m-embed-v2
    
    def validate(self) -> None:
        """Validate Qdrant configuration."""
        if not self.url:
            raise ValueError("QDRANT_URL is required")
        if self.embedding_dim <= 0:
            raise ValueError("EMBEDDING_DIM must be positive")

@dataclass
class DocumentProcessingConfig:
    """Document processing configuration."""
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_tokens: int = 2048  # NVIDIA embedding model limit
    batch_size: int = 10
    
    def validate(self) -> None:
        """Validate processing configuration."""
        if self.chunk_size > self.max_tokens:
            raise ValueError("chunk_size cannot exceed max_tokens")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

@dataclass
class RetrievalConfig:
    """Retrieval and reranking configuration."""
    initial_top_k: int = 50  # Initial vector search results
    rerank_top_k: int = 10   # Final results after reranking
    score_threshold: float = 0.0
    
    def validate(self) -> None:
        """Validate retrieval configuration."""
        if self.rerank_top_k > self.initial_top_k:
            raise ValueError("rerank_top_k cannot exceed initial_top_k")
        if not 0 <= self.score_threshold <= 1:
            raise ValueError("score_threshold must be between 0 and 1")

@dataclass
class Config:
    """Main configuration class aggregating all sub-configs."""
    nvidia: NvidiaAPIConfig
    qdrant: QdrantConfig
    processing: DocumentProcessingConfig
    retrieval: RetrievalConfig
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.
        Implements Factory pattern for config creation.
        """
        nvidia = NvidiaAPIConfig(
            api_key=os.getenv("NVIDIA_API_KEY", ""),
            base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        )
        
        qdrant = QdrantConfig(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name=os.getenv("COLLECTION_NAME", "customer_support_docs"),
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "300"))
        )
        
        processing = DocumentProcessingConfig(
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            batch_size=int(os.getenv("BATCH_SIZE", "10"))
        )
        
        retrieval = RetrievalConfig(
            initial_top_k=int(os.getenv("INITIAL_TOP_K", "50")),
            rerank_top_k=int(os.getenv("RERANK_TOP_K", "10")),
            score_threshold=float(os.getenv("SCORE_THRESHOLD", "0.0"))
        )
        
        return cls(
            nvidia=nvidia,
            qdrant=qdrant,
            processing=processing,
            retrieval=retrieval
        )
    
    def validate(self) -> None:
        """Validate all configuration components."""
        self.nvidia.validate()
        self.qdrant.validate()
        self.processing.validate()
        self.retrieval.validate()

# Create logs directory
Path("logs").mkdir(exist_ok=True)
