"""Recursive text chunker for document processing."""
import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .interfaces import IChunker, Document

logger = logging.getLogger(__name__)

class RecursiveChunker(IChunker):
    """Chunk text using recursive character splitting."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize recursive chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create splitter with markdown-aware separators
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",
                "? ",
                ", ",    # Clause breaks
                " ",     # Words
                ""       # Characters (fallback)
            ],
            is_separator_regex=False
        )
        
        logger.info(f"Initialized RecursiveChunker (size={chunk_size}, overlap={chunk_overlap})")
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Base metadata to attach to all chunks
            
        Returns:
            List of Document objects with chunks and metadata
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for chunking")
            return []
        
        # Split text into chunks
        chunks = self.splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            # Add chunk-specific metadata
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            }
            
            doc = Document(
                content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} chunks from {len(text)} characters")
        return documents
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of dicts with 'text' and 'metadata' keys
            
        Returns:
            List of chunked Document objects
        """
        all_chunks = []
        
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            chunks = self.chunk(text, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks
