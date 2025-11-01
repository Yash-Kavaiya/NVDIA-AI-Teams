"""Document chunking module using Docling's HierarchicalChunker."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from docling.datamodel.document import DoclingDocument
from docling.chunking import HierarchicalChunker

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""
    
    chunk_id: str
    chunk_index: int
    source_filename: str
    source_filepath: str
    total_chunks: int
    char_count: int
    original_metadata: Dict[str, Any]


@dataclass
class DocumentChunk:
    """Represents a chunk of document text with metadata."""
    
    text: str
    metadata: ChunkMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary format.
        
        Returns:
            Dictionary representation of the chunk
        """
        return {
            "text": self.text,
            "chunk_id": self.metadata.chunk_id,
            "chunk_index": self.metadata.chunk_index,
            "source_filename": self.metadata.source_filename,
            "source_filepath": self.metadata.source_filepath,
            "total_chunks": self.metadata.total_chunks,
            "char_count": self.metadata.char_count,
            "original_metadata": self.metadata.original_metadata
        }


class DocumentChunker:
    """Handles document chunking using Docling's HierarchicalChunker.
    
    Single Responsibility: Split documents into semantic chunks.
    """
    
    def __init__(self):
        """Initialize the document chunker."""
        self.chunker = HierarchicalChunker()
        logger.info("DocumentChunker initialized with HierarchicalChunker")
    
    def chunk_document(
        self, 
        document: DoclingDocument,
        source_filename: str,
        source_filepath: str,
        original_metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Chunk a single Docling document.
        
        Args:
            document: DoclingDocument to chunk
            source_filename: Name of the source file
            source_filepath: Path to the source file
            original_metadata: Optional metadata from the original document
            
        Returns:
            List of DocumentChunk objects
        """
        try:
            logger.info(f"Chunking document: {source_filename}")
            
            # Perform chunking
            doc_chunks = list(self.chunker.chunk(document))
            total_chunks = len(doc_chunks)
            
            logger.info(f"Created {total_chunks} chunks from {source_filename}")
            
            # Convert to DocumentChunk objects
            result_chunks = []
            
            for idx, chunk in enumerate(doc_chunks):
                chunk_text = chunk.text
                char_count = len(chunk_text)
                
                # Create unique chunk ID
                chunk_id = f"{source_filename}_chunk_{idx}"
                
                metadata = ChunkMetadata(
                    chunk_id=chunk_id,
                    chunk_index=idx,
                    source_filename=source_filename,
                    source_filepath=source_filepath,
                    total_chunks=total_chunks,
                    char_count=char_count,
                    original_metadata=original_metadata or {}
                )
                
                result_chunks.append(DocumentChunk(
                    text=chunk_text,
                    metadata=metadata
                ))
            
            return result_chunks
            
        except Exception as e:
            logger.error(f"Error chunking document {source_filename}: {e}", exc_info=True)
            return []
    
    def chunk_documents(
        self, 
        extracted_data: List[Dict[str, Any]]
    ) -> List[DocumentChunk]:
        """Chunk multiple documents.
        
        Args:
            extracted_data: List of dictionaries from DocumentExtractor
            
        Returns:
            List of all DocumentChunk objects from all documents
        """
        all_chunks = []
        
        for data in extracted_data:
            # Skip documents that failed processing
            if data["document"] is None or not data["metadata"]["success"]:
                logger.warning(
                    f"Skipping failed document: {data['metadata']['filename']}"
                )
                continue
            
            chunks = self.chunk_document(
                document=data["document"],
                source_filename=data["metadata"]["filename"],
                source_filepath=data["metadata"]["filepath"],
                original_metadata=data["metadata"]
            )
            
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        return all_chunks


class ChunkProcessor:
    """Processes and filters chunks based on quality criteria.
    
    Single Responsibility: Filter and validate chunks.
    """
    
    def __init__(
        self, 
        min_chunk_length: int = 50,
        max_chunk_length: int = 10000
    ):
        """Initialize chunk processor.
        
        Args:
            min_chunk_length: Minimum character length for valid chunks
            max_chunk_length: Maximum character length for valid chunks
        """
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
        logger.info(
            f"ChunkProcessor initialized (min: {min_chunk_length}, max: {max_chunk_length})"
        )
    
    def filter_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Filter chunks based on quality criteria.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            Filtered list of DocumentChunk objects
        """
        filtered = []
        
        for chunk in chunks:
            # Check length constraints
            if chunk.metadata.char_count < self.min_chunk_length:
                logger.debug(
                    f"Skipping chunk {chunk.metadata.chunk_id}: too short "
                    f"({chunk.metadata.char_count} chars)"
                )
                continue
            
            if chunk.metadata.char_count > self.max_chunk_length:
                logger.warning(
                    f"Skipping chunk {chunk.metadata.chunk_id}: too long "
                    f"({chunk.metadata.char_count} chars)"
                )
                continue
            
            # Check if chunk has meaningful content (not just whitespace)
            if not chunk.text.strip():
                logger.debug(f"Skipping chunk {chunk.metadata.chunk_id}: empty content")
                continue
            
            filtered.append(chunk)
        
        removed = len(chunks) - len(filtered)
        logger.info(f"Filtered {removed} chunks, {len(filtered)} remaining")
        
        return filtered
    
    def prepare_for_embedding(
        self, 
        chunks: List[DocumentChunk]
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for embedding generation.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            List of dictionaries ready for embedding
        """
        prepared = []
        
        for chunk in chunks:
            prepared.append({
                "text": chunk.text,
                "metadata": chunk.metadata.original_metadata,
                "chunk_id": chunk.metadata.chunk_id,
                "chunk_index": chunk.metadata.chunk_index,
                "source_filename": chunk.metadata.source_filename,
                "source_filepath": chunk.metadata.source_filepath,
                "char_count": chunk.metadata.char_count
            })
        
        logger.info(f"Prepared {len(prepared)} chunks for embedding")
        
        return prepared
