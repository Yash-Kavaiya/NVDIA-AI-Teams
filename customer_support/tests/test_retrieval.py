"""Test cases for retrieval functionality."""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

from config.config import Config
from src.retrieval import RetrievalPipeline

# Load test configuration
@pytest.fixture
def config():
    """Create test configuration."""
    os.environ["NVIDIA_API_KEY"] = "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"
    os.environ["NVIDIA_EMBEDDING_URL"] = "https://integrate.api.nvidia.com/v1/embeddings"
    os.environ["NVIDIA_RERANK_URL"] = "https://integrate.api.nvidia.com/v1/ranking"
    os.environ["QDRANT_URL"] = "http://localhost:6333"
    os.environ["COLLECTION_NAME"] = "test_collection"
    os.environ["EMBEDDING_DIM"] = "2048"
    return Config.from_env()

@pytest.fixture
def mock_embedding():
    """Create mock embedding."""
    return np.random.randn(2048).tolist()  # Match embedding dimension

@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    return [
        {
            "id": 1,
            "score": 0.9,
            "text": "This is a test passage about retail compliance.",
            "chunk_id": "doc1-1",
            "source_filename": "test.pdf",
            "metadata": {"page": 1}
        },
        {
            "id": 2,
            "score": 0.8,
            "text": "Another test passage about regulations.",
            "chunk_id": "doc1-2",
            "source_filename": "test.pdf",
            "metadata": {"page": 2}
        }
    ]

@pytest.mark.asyncio
async def test_search_with_reranking(config, mock_embedding, mock_search_results):
    """Test search functionality with reranking."""
    
    # Create retrieval pipeline with mocked dependencies
    pipeline = RetrievalPipeline(config)
    
    # Mock embedding generation
    pipeline.embedding_generator.generate_embedding = AsyncMock(
        return_value=mock_embedding
    )
    
    # Mock Qdrant search
    pipeline.qdrant_manager.search = Mock(return_value=mock_search_results)
    
    # Mock aiohttp session
    session = AsyncMock()
    session.post = AsyncMock()
    session.close = AsyncMock()
    
    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"scores": [0.95, 0.85]})
    session.post.return_value = mock_response
    
    # Set session
    pipeline.session = session
    
    results = await pipeline.search(
        query="test query",
        top_k=2,
        rerank=True
    )
    
    # Verify results
    assert len(results) == 2
    assert results[0]["rerank_score"] == 0.95  # Highest rerank score
    assert results[1]["rerank_score"] == 0.85
    assert results[0]["text"] == mock_search_results[0]["text"]
    
    # Verify Qdrant was searched with correct parameters
    pipeline.qdrant_manager.search.assert_called_once()
    call_args = pipeline.qdrant_manager.search.call_args[1]
    assert call_args["top_k"] == 4  # 2 * top_k because reranking=True
    assert call_args["score_threshold"] is None
    
    # Verify reranking was called
    pipeline.session.post.assert_called_once()
    
    # Clean up
    await pipeline.close()