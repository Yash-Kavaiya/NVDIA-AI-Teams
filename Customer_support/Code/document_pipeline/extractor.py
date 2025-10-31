"""Document extractor using Docling for OCR."""
import logging
from pathlib import Path
from typing import Optional
from docling.document_converter import DocumentConverter
from .interfaces import IDocumentExtractor

logger = logging.getLogger(__name__)

class DoclingExtractor(IDocumentExtractor):
    """Extract text from PDFs using Docling OCR."""
    
    def __init__(self):
        """Initialize Docling document converter."""
        self.converter = DocumentConverter()
        logger.info("Initialized Docling document converter")
    
    def extract(self, file_path: str) -> str:
        """
        Extract text from a PDF file using Docling.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If extraction fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"Only PDF files are supported, got: {path.suffix}")
        
        try:
            logger.info(f"Extracting text from: {path.name}")
            
            # Convert document using Docling
            result = self.converter.convert(str(path))
            
            # Extract markdown text (Docling preserves structure)
            text = result.document.export_to_markdown()
            
            if not text or len(text.strip()) == 0:
                logger.warning(f"No text extracted from {path.name}")
                return ""
            
            logger.info(f"Extracted {len(text)} characters from {path.name}")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract from {path.name}: {e}")
            raise ValueError(f"Extraction failed: {e}")
    
    def extract_with_metadata(self, file_path: str) -> dict:
        """
        Extract text and metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with 'text' and 'metadata' keys
        """
        path = Path(file_path)
        text = self.extract(file_path)
        
        metadata = {
            "source": path.name,
            "file_path": str(path.absolute()),
            "file_size": path.stat().st_size,
            "char_count": len(text)
        }
        
        return {
            "text": text,
            "metadata": metadata
        }
