"""
Document Processing Pipeline

A production-grade pipeline for PDF extraction, embedding generation,
and semantic search with reranking. Built with SOLID principles.

Key Components:
- DoclingExtractor: PDF text extraction
- OverlapTextChunker: Text chunking with overlap
- NvidiaEmbeddingGenerator: NVIDIA API embeddings
- QdrantVectorDB: Vector database operations
- NvidiaReranker: Result reranking
- RetrievalPipeline: Search orchestration
- DocumentProcessor: Processing orchestration

Usage:
    from document_pipeline import DocumentProcessor, RetrievalPipeline
    
    # Process documents
    processor = DocumentProcessor(...)
    stats = await processor.process_directory("../Customer_support/Data")
    
    # Search documents
    retrieval = RetrievalPipeline(...)
    results = await retrieval.retrieve("query")
"""

__version__ = "1.0.0"
__author__ = "NVIDIA AI Teams"

from .config import Config
from .interfaces import (
    IDocumentExtractor,
    ITextChunker,
    IEmbeddingGenerator,
    IVectorDatabase,
    IReranker,
    IRetrievalPipeline,
    IDocumentProcessor,
    Document,
    DocumentChunk,
    SearchResult
)
from .extractor import DoclingExtractor
from .chunker import OverlapTextChunker
from .embedding_generator import NvidiaEmbeddingGenerator
from .vector_db import QdrantVectorDB
from .reranker import NvidiaReranker
from .retrieval_pipeline import RetrievalPipeline
from .document_processor import DocumentProcessor

__all__ = [
    "Config",
    "IDocumentExtractor",
    "ITextChunker",
    "IEmbeddingGenerator",
    "IVectorDatabase",
    "IReranker",
    "IRetrievalPipeline",
    "IDocumentProcessor",
    "Document",
    "DocumentChunk",
    "SearchResult",
    "DoclingExtractor",
    "OverlapTextChunker",
    "NvidiaEmbeddingGenerator",
    "QdrantVectorDB",
    "NvidiaReranker",
    "RetrievalPipeline",
    "DocumentProcessor",
]
