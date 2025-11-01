"""Main pipeline for loading, processing, and storing customer support documents."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.config import Config
from src.data_ingestion import PDFProcessor, DocumentExtractor
from src.chunking import DocumentChunker, ChunkProcessor
from src.embedding import EmbeddingGenerator, DocumentEmbedder
from src.qdrant_manager import QdrantManager

logger = logging.getLogger(__name__)


class CustomerSupportPipeline:
    """Main pipeline orchestrating document processing workflow.
    
    Single Responsibility: Coordinate all pipeline stages.
    """
    
    def __init__(self, config: Config):
        """Initialize the pipeline with all required components.
        
        Args:
            config: Main configuration object (Dependency Injection)
        """
        self.config = config
        
        # Initialize components
        logger.info("Initializing pipeline components")
        
        # Data ingestion
        pdf_processor = PDFProcessor(generate_page_images=False)
        self.document_extractor = DocumentExtractor(pdf_processor)
        
        # Chunking
        self.document_chunker = DocumentChunker()
        self.chunk_processor = ChunkProcessor(
            min_chunk_length=50,
            max_chunk_length=10000
        )
        
        # Embedding
        embedding_generator = EmbeddingGenerator(config.nvidia)
        self.document_embedder = DocumentEmbedder(
            embedding_generator,
            batch_size=config.processing.batch_size
        )
        
        # Database
        self.qdrant_manager = QdrantManager(config.qdrant)
        
        logger.info("Pipeline initialized successfully")
    
    def process_directory(self, directory_path: Path) -> Dict[str, Any]:
        """Process all PDFs in a directory through the complete pipeline.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary with pipeline statistics
        """
        logger.info(f"Starting pipeline for directory: {directory_path}")
        
        stats = {
            "documents_processed": 0,
            "documents_failed": 0,
            "total_chunks": 0,
            "chunks_embedded": 0,
            "chunks_stored": 0
        }
        
        # Stage 1: Extract documents
        logger.info("Stage 1: Extracting documents")
        extracted_data = self.document_extractor.extract_from_directory(directory_path)
        
        stats["documents_processed"] = sum(
            1 for d in extracted_data if d["metadata"]["success"]
        )
        stats["documents_failed"] = sum(
            1 for d in extracted_data if not d["metadata"]["success"]
        )
        
        logger.info(
            f"Extracted {stats['documents_processed']} documents "
            f"({stats['documents_failed']} failed)"
        )
        
        # Stage 2: Chunk documents
        logger.info("Stage 2: Chunking documents")
        chunks = self.document_chunker.chunk_documents(extracted_data)
        stats["total_chunks"] = len(chunks)
        
        logger.info(f"Created {stats['total_chunks']} chunks")
        
        # Stage 3: Filter and prepare chunks
        logger.info("Stage 3: Filtering chunks")
        filtered_chunks = self.chunk_processor.filter_chunks(chunks)
        prepared_chunks = self.chunk_processor.prepare_for_embedding(filtered_chunks)
        
        logger.info(f"Prepared {len(prepared_chunks)} chunks for embedding")
        
        # Stage 4: Generate embeddings
        logger.info("Stage 4: Generating embeddings")
        embedded_chunks = self.document_embedder.embed_chunks(prepared_chunks)
        stats["chunks_embedded"] = len(embedded_chunks)
        
        logger.info(f"Generated {stats['chunks_embedded']} embeddings")
        
        # Stage 5: Store in Qdrant
        logger.info("Stage 5: Storing in Qdrant")
        stored_count = self.qdrant_manager.insert_chunks(embedded_chunks)
        stats["chunks_stored"] = stored_count
        
        logger.info(f"Stored {stats['chunks_stored']} chunks in Qdrant")
        
        # Final summary
        logger.info("Pipeline complete!")
        logger.info(f"Summary: {stats}")
        
        return stats
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single PDF file through the complete pipeline.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with pipeline statistics
        """
        logger.info(f"Starting pipeline for file: {file_path}")
        
        stats = {
            "documents_processed": 0,
            "documents_failed": 0,
            "total_chunks": 0,
            "chunks_embedded": 0,
            "chunks_stored": 0
        }
        
        # Stage 1: Extract document
        logger.info("Stage 1: Extracting document")
        extracted_data = self.document_extractor.extract_from_file(file_path)
        
        if extracted_data["metadata"]["success"]:
            stats["documents_processed"] = 1
        else:
            stats["documents_failed"] = 1
            logger.error("Document extraction failed")
            return stats
        
        # Stage 2: Chunk document
        logger.info("Stage 2: Chunking document")
        chunks = self.document_chunker.chunk_document(
            document=extracted_data["document"],
            source_filename=extracted_data["metadata"]["filename"],
            source_filepath=extracted_data["metadata"]["filepath"],
            original_metadata=extracted_data["metadata"]
        )
        stats["total_chunks"] = len(chunks)
        
        # Stage 3: Filter and prepare chunks
        logger.info("Stage 3: Filtering chunks")
        filtered_chunks = self.chunk_processor.filter_chunks(chunks)
        prepared_chunks = self.chunk_processor.prepare_for_embedding(filtered_chunks)
        
        # Stage 4: Generate embeddings
        logger.info("Stage 4: Generating embeddings")
        embedded_chunks = self.document_embedder.embed_chunks(prepared_chunks)
        stats["chunks_embedded"] = len(embedded_chunks)
        
        # Stage 5: Store in Qdrant
        logger.info("Stage 5: Storing in Qdrant")
        stored_count = self.qdrant_manager.insert_chunks(embedded_chunks)
        stats["chunks_stored"] = stored_count
        
        logger.info(f"Pipeline complete! Stats: {stats}")
        
        return stats
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the Qdrant collection.
        
        Returns:
            Dictionary with collection statistics
        """
        return self.qdrant_manager.get_collection_info()


class SearchPipeline:
    """Pipeline for searching and retrieving documents.
    
    Single Responsibility: Coordinate search and retrieval operations.
    """
    
    def __init__(self, config: Config):
        """Initialize search pipeline.
        
        Args:
            config: Main configuration object
        """
        self.config = config
        
        # Initialize components
        embedding_generator = EmbeddingGenerator(config.nvidia)
        self.document_embedder = DocumentEmbedder(embedding_generator)
        self.qdrant_manager = QdrantManager(config.qdrant)
        
        logger.info("SearchPipeline initialized")
    
    def search(
        self, 
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search for documents relevant to a query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with text and metadata
        """
        logger.info(f"Searching for query: {query}")
        
        # Generate query embedding
        query_embedding = self.document_embedder.embed_query(query)
        
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []
        
        # Search in Qdrant
        results = self.qdrant_manager.search(
            query_vector=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        logger.info(f"Found {len(results)} results")
        
        return results


def setup_logging(log_file: Path = None):
    """Setup logging configuration.
    
    Args:
        log_file: Optional path to log file
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )
