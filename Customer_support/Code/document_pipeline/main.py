"""Main document processing pipeline."""
import logging
import sys
from pathlib import Path
from typing import List

from config import Config
from extractor import DoclingExtractor
from chunker import RecursiveChunker
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker
from retrieval_pipeline import RetrievalPipeline
from interfaces import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DocumentPipeline:
    """Complete document ingestion and retrieval pipeline."""
    
    def __init__(self, config: Config):
        """
        Initialize pipeline components.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        
        self.extractor = DoclingExtractor()
        
        self.chunker = RecursiveChunker(
            chunk_size=config.processing.chunk_size,
            chunk_overlap=config.processing.chunk_overlap
        )
        
        self.embedding_generator = NvidiaEmbeddingGenerator(
            api_key=config.nvidia.api_key,
            model=config.nvidia.embedding_model
        )
        
        self.vector_db = QdrantVectorDB(
            url=config.qdrant.url,
            collection_name=config.qdrant.collection_name,
            vector_size=config.qdrant.embedding_dim
        )
        
        self.reranker = NvidiaReranker(
            api_key=config.nvidia.api_key,
            model=config.nvidia.reranker_model
        )
        
        self.retrieval_pipeline = RetrievalPipeline(
            embedding_generator=self.embedding_generator,
            vector_db=self.vector_db,
            reranker=self.reranker,
            config=config.retrieval
        )
        
        logger.info("Pipeline initialized successfully")
    
    def process_documents(self, pdf_dir: Path) -> int:
        """
        Process all PDF documents in a directory.
        
        Args:
            pdf_dir: Directory containing PDF files
            
        Returns:
            Number of chunks processed
        """
        logger.info(f"Processing PDFs from: {pdf_dir}")
        
        # Find all PDF files
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return 0
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Step 1: Extract text from PDFs
        logger.info("Step 1: Extracting text from PDFs...")
        extracted_docs = []
        
        for pdf_file in pdf_files:
            try:
                doc = self.extractor.extract_with_metadata(str(pdf_file))
                extracted_docs.append(doc)
                logger.info(f"✓ Extracted: {pdf_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to extract {pdf_file.name}: {e}")
                continue
        
        if not extracted_docs:
            logger.error("No documents were successfully extracted")
            return 0
        
        logger.info(f"Successfully extracted {len(extracted_docs)} documents")
        
        # Step 2: Chunk documents
        logger.info("Step 2: Chunking documents...")
        chunks = self.chunker.chunk_documents(extracted_docs)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings...")
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_generator.embed_documents_batch(
            texts,
            batch_size=self.config.processing.batch_size
        )
        
        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        
        # Step 4: Store in vector database
        logger.info("Step 4: Storing in Qdrant...")
        
        # Create collection if it doesn't exist
        if not self.vector_db.collection_exists():
            logger.info("Creating collection...")
            self.vector_db.create_collection()
        
        self.vector_db.upsert_documents(chunks)
        logger.info(f"Stored {len(chunks)} chunks in vector database")
        
        # Print collection info
        info = self.vector_db.get_collection_info()
        logger.info(f"Collection info: {info}")
        
        return len(chunks)
    
    def search(self, query: str) -> dict:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        return self.retrieval_pipeline.search_with_details(query)

def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("Starting Document Pipeline")
    logger.info("=" * 80)
    
    try:
        # Load and validate configuration
        config = Config.from_env()
        config.validate()
        logger.info("Configuration loaded and validated")
        
        # Initialize pipeline
        pipeline = DocumentPipeline(config)
        
        # Process documents
        logger.info(f"Data directory: {config.data_dir}")
        num_chunks = pipeline.process_documents(config.data_dir)
        
        logger.info("=" * 80)
        logger.info(f"Pipeline complete! Processed {num_chunks} chunks")
        logger.info("=" * 80)
        
        # Run example search if documents were processed
        if num_chunks > 0:
            logger.info("\nRunning example search...")
            query = "What is the Consumer Product Safety Commission?"
            results = pipeline.search(query)
            
            logger.info(f"\nQuery: {query}")
            logger.info(f"Found {results['num_results']} results:\n")
            
            for result in results['results']:
                logger.info(f"Rank {result['rank']} (Score: {result['score']:.4f})")
                logger.info(f"Source: {result['metadata'].get('source', 'Unknown')}")
                logger.info(f"Content: {result['content'][:200]}...")
                logger.info("-" * 80)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
