"""Configuration module for customer support document pipeline."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class NVIDIAConfig:
    """NVIDIA API configuration."""
    
    api_key: str
    embedding_url: str
    rerank_url: str
    embedding_model: str
    rerank_model: str
    request_timeout: int = 60
    
    def __post_init__(self):
        """Validate required configuration."""
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError("NVIDIA_API_KEY must be set in .env file")
        if not self.api_key.startswith("nvapi-"):
            raise ValueError("NVIDIA_API_KEY must start with 'nvapi-'")


@dataclass
class QdrantConfig:
    """Qdrant database configuration."""
    
    url: str
    collection_name: str
    embedding_dim: int
    
    def __post_init__(self):
        """Validate required configuration."""
        if not self.url:
            raise ValueError("QDRANT_URL must be set in .env file")
        if self.embedding_dim <= 0:
            raise ValueError("EMBEDDING_DIM must be positive")


@dataclass
class ProcessingConfig:
    """Document processing configuration."""
    
    chunk_size: int
    chunk_overlap: int
    batch_size: int
    
    def __post_init__(self):
        """Validate required configuration."""
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("CHUNK_OVERLAP must be non-negative")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        if self.batch_size <= 0:
            raise ValueError("BATCH_SIZE must be positive")


@dataclass
class Config:
    """Main configuration class."""
    
    nvidia: NVIDIAConfig
    qdrant: QdrantConfig
    processing: ProcessingConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            nvidia=NVIDIAConfig(
                api_key=os.getenv("NVIDIA_API_KEY", ""),
                embedding_url=os.getenv("NVIDIA_EMBEDDING_URL", ""),
                rerank_url=os.getenv("NVIDIA_RERANK_URL", ""),
                embedding_model=os.getenv("EMBEDDING_MODEL", "nvidia/llama-3.2-nemoretriever-300m-embed-v2"),
                rerank_model=os.getenv("RERANK_MODEL", "nvidia/llama-3.2-nv-rerankqa-1b-v2"),
                request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60"))
            ),
            qdrant=QdrantConfig(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                collection_name=os.getenv("COLLECTION_NAME", "customer_support_docs"),
                embedding_dim=int(os.getenv("EMBEDDING_DIM", "2048"))
            ),
            processing=ProcessingConfig(
                chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
                batch_size=int(os.getenv("BATCH_SIZE", "10"))
            )
        )
