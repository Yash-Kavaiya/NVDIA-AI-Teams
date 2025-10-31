"""
Document processing orchestrator.
Implements Facade pattern - provides simple interface to complex subsystem.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from interfaces import (
    IDocumentProcessor,
    IDocumentExtractor,
    ITextChunker,
    IEmbeddingGenerator,
    IVectorDatabase
)

logger = logging.getLogger(__name__)

class DocumentProcessor(IDocumentProcessor):
    """
    Orchestrates the complete document processing pipeline.
    
    Responsibilities:
    1. Extract text from PDFs (via Docling)
    2. Chunk text with overlap
    3. Generate embeddings for chunks
    4. Store in vector database
    
    This is the Facade - it coordinates multiple subsystems
    but delegates actual work to specialized components.
    """
    
    def __init__(
        self,
        extractor: IDocumentExtractor,
        chunker: ITextChunker,
        embedder: IEmbeddingGenerator,
        vector_db: IVectorDatabase
    ):
        """
        Initialize document processor.
        
        Args:
            extractor: Document extractor
            chunker: Text chunker
            embedder: Embedding generator
            vector_db: Vector database
        """
        self.extractor = extractor
        self.chunker = chunker
        self.embedder = embedder
        self.vector_db = vector_db
        logger.info("DocumentProcessor initialized")
    
    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            Processing statistics
        """
        start_time = datetime.now()
        
        # Find all PDF files
        pdf_dir = Path(directory_path)
        if not pdf_dir.exists():
            logger.error(f"Directory not found: {directory_path}")
            return {"error": "Directory not found"}
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return {"error": "No PDF files found"}
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Ensure collection exists
        await self.vector_db.create_collection()
        
        # Process each file
        stats = {
            "total_files": len(pdf_files),
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "files_processed": []
        }
        
        for pdf_file in pdf_files:
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing: {pdf_file.name}")
            logger.info(f"{'='*80}")
            
            file_stats = await self.process_single_file(str(pdf_file))
            
            if file_stats["success"]:
                stats["successful_files"] += 1
                stats["total_chunks"] += file_stats["chunks"]
                stats["total_embeddings"] += file_stats["embeddings"]
            else:
                stats["failed_files"] += 1
            
            stats["files_processed"].append({
                "filename": pdf_file.name,
                "success": file_stats["success"],
                "chunks": file_stats["chunks"],
                "embeddings": file_stats["embeddings"]
            })
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        stats["duration_seconds"] = duration
        
        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("PROCESSING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total files: {stats['total_files']}")
        logger.info(f"Successful: {stats['successful_files']}")
        logger.info(f"Failed: {stats['failed_files']}")
        logger.info(f"Total chunks: {stats['total_chunks']}")
        logger.info(f"Total embeddings: {stats['total_embeddings']}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"{'='*80}\n")
        
        return stats
    
    async def process_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            File processing statistics
        """
        file_stats = {
            "success": False,
            "chunks": 0,
            "embeddings": 0,
            "error": None
        }
        
        try:
            # Step 1: Extract text from PDF
            logger.info("Step 1/4: Extracting text from PDF...")
            documents = await self.extractor.extract(file_path)
            
            if not documents:
                logger.warning("No text extracted from PDF")
                file_stats["error"] = "No text extracted"
                return file_stats
            
            logger.info(f"✓ Extracted {len(documents)} document(s)")
            
            # Step 2: Chunk documents
            logger.info("Step 2/4: Chunking documents...")
            all_chunks = []
            for doc in documents:
                chunks = self.chunker.chunk(doc)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                logger.warning("No chunks created")
                file_stats["error"] = "No chunks created"
                return file_stats
            
            logger.info(f"✓ Created {len(all_chunks)} chunks")
            file_stats["chunks"] = len(all_chunks)
            
            # Step 3: Generate embeddings
            logger.info("Step 3/4: Generating embeddings...")
            texts = [chunk.content for chunk in all_chunks]
            embeddings = await self.embedder.generate_batch_embeddings(
                texts=texts,
                input_type="passage"  # Documents are passages, not queries
            )
            
            # Count successful embeddings
            valid_pairs = [
                (chunk, emb) 
                for chunk, emb in zip(all_chunks, embeddings) 
                if emb is not None
            ]
            
            if not valid_pairs:
                logger.warning("No embeddings generated")
                file_stats["error"] = "No embeddings generated"
                return file_stats
            
            logger.info(f"✓ Generated {len(valid_pairs)} embeddings")
            file_stats["embeddings"] = len(valid_pairs)
            
            # Step 4: Store in vector database
            logger.info("Step 4/4: Storing in vector database...")
            valid_chunks = [pair[0] for pair in valid_pairs]
            valid_embeddings = [pair[1] for pair in valid_pairs]
            
            success = await self.vector_db.upsert_documents(
                chunks=valid_chunks,
                embeddings=valid_embeddings
            )
            
            if success:
                logger.info("✓ Successfully stored in database")
                file_stats["success"] = True
            else:
                logger.error("✗ Failed to store in database")
                file_stats["error"] = "Database storage failed"
            
            return file_stats
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            file_stats["error"] = str(e)
            return file_stats
