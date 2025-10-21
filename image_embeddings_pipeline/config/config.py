"""Configuration management module."""
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class NvidiaConfig:
    """NVIDIA API configuration."""
    api_key: str
    embedding_url: str
    model: str = "nvidia/nv-embed-v1"
    encoding_format: str = "float"
    
    @property
    def headers(self) -> dict:
        """Get API headers."""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

@dataclass
class QdrantConfig:
    """Qdrant database configuration."""
    url: str
    collection_name: str
    embedding_dim: int
    
@dataclass
class ProcessingConfig:
    """Image processing configuration."""
    batch_size: int
    concurrent_downloads: int
    concurrent_embeddings: int
    image_max_size: int
    image_quality: int
    request_timeout: int

@dataclass
class Config:
    """Main configuration class."""
    nvidia: NvidiaConfig
    qdrant: QdrantConfig
    processing: ProcessingConfig
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        nvidia = NvidiaConfig(
            api_key=os.getenv("NVIDIA_API_KEY", ""),
            embedding_url=os.getenv("NVIDIA_EMBEDDING_URL", "")
        )
        
        qdrant = QdrantConfig(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name=os.getenv("COLLECTION_NAME", "image_embeddings"),
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "4096"))
        )
        
        processing = ProcessingConfig(
            batch_size=int(os.getenv("BATCH_SIZE", "25")),
            concurrent_downloads=int(os.getenv("CONCURRENT_DOWNLOADS", "10")),
            concurrent_embeddings=int(os.getenv("CONCURRENT_EMBEDDINGS", "5")),
            image_max_size=int(os.getenv("IMAGE_MAX_SIZE", "128")),
            image_quality=int(os.getenv("IMAGE_QUALITY", "70")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60"))
        )
        
        return cls(nvidia=nvidia, qdrant=qdrant, processing=processing)
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.nvidia.api_key:
            raise ValueError("NVIDIA_API_KEY is required")
        if not self.nvidia.embedding_url:
            raise ValueError("NVIDIA_EMBEDDING_URL is required")
        if self.processing.batch_size < 1:
            raise ValueError("BATCH_SIZE must be >= 1")
        if self.qdrant.embedding_dim < 1:
            raise ValueError("EMBEDDING_DIM must be >= 1")

# Create logs directory
Path("logs").mkdir(exist_ok=True)