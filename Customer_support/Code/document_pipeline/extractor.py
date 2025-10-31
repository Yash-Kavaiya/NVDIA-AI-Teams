"""
Document extraction using Docling library.
Implements Single Responsibility Principle - only handles document extraction.
"""
import logging
from typing import List
from pathlib import Path
from docling.document_converter import DocumentConverter

from interfaces import IDocumentExtractor, Document

logger = logging.getLogger(__name__)

class DoclingExtractor(IDocumentExtractor):
    """
    Extracts text and metadata from PDF documents using Docling.
    
    Docling provides structured extraction with table detection,
    page numbers, and maintains document hierarchy.
    """
    
    def __init__(self):
        """Initialize Docling converter."""
        self.converter = DocumentConverter()
        logger.info("DoclingExtractor initialized")
    
    async def extract(self, file_path: str) -> List[Document]:
        """
        Extract text from PDF using Docling.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of Document objects (one per page or section)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []
            
            logger.info(f"Extracting: {path.name}")
            
            # Convert document
            result = self.converter.convert(str(path))
            
            # Extract text with page information
            documents = []

            # docling's return shape can vary between versions. Normalize access.
            doc_obj = getattr(result, 'document', result)

            # Get markdown output (preserves structure) if available
            if hasattr(doc_obj, 'export_to_markdown'):
                try:
                    full_text = doc_obj.export_to_markdown()
                except Exception:
                    full_text = str(doc_obj)
            else:
                full_text = str(doc_obj)

            # Split by pages if available (pages may be objects or dicts)
            pages = getattr(doc_obj, 'pages', None)
            if pages:
                for page_num, page in enumerate(pages, start=1):
                    if hasattr(page, 'export_to_markdown'):
                        try:
                            page_text = page.export_to_markdown()
                        except Exception:
                            page_text = str(page)
                    elif isinstance(page, dict):
                        # Try common keys
                        page_text = page.get('text') or page.get('content') or str(page)
                    else:
                        page_text = str(page)

                    if page_text and page_text.strip():
                        doc = Document(
                            content=page_text,
                            metadata={
                                "filename": path.name,
                                "file_path": str(path),
                                "extraction_method": "docling",
                                "has_tables": self._has_tables(page_text)
                            },
                            source=str(path),
                            page_number=page_num
                        )
                        documents.append(doc)
            else:
                # Fallback: single document
                doc = Document(
                    content=full_text,
                    metadata={
                        "filename": path.name,
                        "file_path": str(path),
                        "extraction_method": "docling"
                    },
                    source=str(path),
                    page_number=None
                )
                documents.append(doc)
            
            logger.info(f"✓ Extracted {len(documents)} page(s) from {path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"✗ Error extracting {file_path}: {e}")
            return []
    
    def _has_tables(self, text: str) -> bool:
        """Check if text contains markdown tables."""
        lines = text.split('\n')
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                return True
        return False
