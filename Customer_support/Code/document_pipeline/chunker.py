"""
Text chunking with overlap for better context preservation.
Implements Single Responsibility Principle - only handles text chunking.
"""
import logging
from typing import List
from interfaces import ITextChunker, Document, DocumentChunk
from config import DocumentProcessingConfig

logger = logging.getLogger(__name__)

class OverlapTextChunker(ITextChunker):
    """
    Chunks text with overlap to preserve context at boundaries.
    
    This is crucial for semantic search - context at chunk boundaries
    shouldn't be lost. Overlapping chunks ensure queries matching
    boundary text still retrieve relevant content.
    """
    
    def __init__(self, config: DocumentProcessingConfig):
        """
        Initialize chunker with configuration.
        
        Args:
            config: Document processing configuration
        """
        self.config = config
        self.chunk_size = config.chunk_size
        self.overlap = config.chunk_overlap
        logger.info(f"TextChunker initialized (size={self.chunk_size}, overlap={self.overlap})")
    
    def chunk(self, document: Document) -> List[DocumentChunk]:
        """
        Split document into overlapping chunks.
        
        Strategy:
        1. Split text into words/tokens
        2. Create chunks of specified size
        3. Add overlap from previous chunk
        4. Preserve metadata and page numbers
        
        Args:
            document: Document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        try:
            text = document.content
            if not text.strip():
                logger.warning(f"Empty document from {document.source}")
                return []
            
            # Simple word-based tokenization (can be replaced with proper tokenizer)
            words = text.split()
            
            if len(words) <= self.chunk_size:
                # Document is smaller than chunk size
                chunk = DocumentChunk(
                    content=text,
                    metadata=document.metadata.copy(),
                    chunk_id=0,
                    source=document.source,
                    page_number=document.page_number
                )
                return [chunk]
            
            chunks = []
            start = 0
            chunk_id = 0
            
            while start < len(words):
                # Get chunk with overlap
                end = min(start + self.chunk_size, len(words))
                chunk_words = words[start:end]
                chunk_text = ' '.join(chunk_words)
                
                # Create chunk with metadata
                chunk_metadata = document.metadata.copy()
                chunk_metadata.update({
                    "chunk_id": chunk_id,
                    "total_chunks": -1,  # Will be updated after loop
                    "start_word": start,
                    "end_word": end
                })
                
                chunk = DocumentChunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                    chunk_id=chunk_id,
                    source=document.source,
                    page_number=document.page_number
                )
                chunks.append(chunk)
                
                # Move to next chunk with overlap
                start += (self.chunk_size - self.overlap)
                chunk_id += 1
            
            # Update total_chunks in metadata
            for chunk in chunks:
                chunk.metadata["total_chunks"] = len(chunks)
            
            logger.debug(f"Created {len(chunks)} chunks from {document.source}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking document {document.source}: {e}")
            return []
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        
        For production, use proper tokenizer like tiktoken.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 0.75 words
        words = len(text.split())
        return int(words * 0.75)
