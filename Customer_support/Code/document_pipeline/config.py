"""Configuration management for document pipeline."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class NvidiaConfig:
    """NVIDIA API configuration."""
    api_key: str
    embedding_model: str
    reranker_model: str
    base_url: str = "https://integrate.api.nvidia.com/v1"
    
@dataclass
class QdrantConfig:
    """Qdrant database configuration."""
    url: str
    collection_name: str
    embedding_dim: int
    
@dataclass
class ProcessingConfig:
    """Document processing configuration."""
    chunk_size: int
    chunk_overlap: int
    batch_size: int
    
@dataclass
class RetrievalConfig:
    """Retrieval configuration."""
    top_k: int  # Initial vector search candidates
    rerank_top_n: int  # Final results after reranking
    score_threshold: float
    
@dataclass
class Config:
    """Main configuration class."""
    nvidia: NvidiaConfig
    qdrant: QdrantConfig
    processing: ProcessingConfig
    retrieval: RetrievalConfig
    data_dir: Path
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        nvidia = NvidiaConfig(
            api_key=os.getenv("NVIDIA_API_KEY", ""),
            embedding_model=os.getenv("EMBEDDING_MODEL", "nvidia/llama-3.2-nv-embedqa-1b-v2"),
            reranker_model=os.getenv("RERANKER_MODEL", "nvidia/llama-3.2-nv-rerankqa-1b-v2"),
            base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        )
        
        qdrant = QdrantConfig(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection_name=os.getenv("COLLECTION_NAME", "customer_support_docs"),
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "2048"))  # llama-3.2-nv-embedqa-1b-v2 dimension
        )
        
        processing = ProcessingConfig(
            chunk_size=int(os.getenv("CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            batch_size=int(os.getenv("BATCH_SIZE", "10"))
        )
        
        retrieval = RetrievalConfig(
            top_k=int(os.getenv("TOP_K", "20")),
            rerank_top_n=int(os.getenv("RERANK_TOP_N", "5")),
            score_threshold=float(os.getenv("SCORE_THRESHOLD", "0.3"))
        )
        
        # Data directory relative to this config file
        config_dir = Path(__file__).parent
        data_dir = config_dir.parent.parent / "Data"
        
        return cls(
            nvidia=nvidia,
            qdrant=qdrant,
            processing=processing,
            retrieval=retrieval,
            data_dir=data_dir
        )
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.nvidia.api_key:
            raise ValueError("NVIDIA_API_KEY is required")
        if self.processing.chunk_size < 1:
            raise ValueError("CHUNK_SIZE must be >= 1")
        if self.processing.chunk_overlap >= self.processing.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be < CHUNK_SIZE")
        if self.retrieval.top_k < self.retrieval.rerank_top_n:
            raise ValueError("TOP_K must be >= RERANK_TOP_N")
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {self.data_dir}")

# Create logs directory
Path("logs").mkdir(exist_ok=True)
