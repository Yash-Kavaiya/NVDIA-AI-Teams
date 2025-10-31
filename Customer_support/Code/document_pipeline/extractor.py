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
                except Exception as e:
                    logger.warning(f"Failed to export to markdown: {e}")
                    full_text = str(doc_obj)
            else:
                full_text = str(doc_obj)

            # Check if we got valid text
            if not full_text or len(full_text.strip()) < 10:
                logger.warning(f"No meaningful text extracted from {path.name}")
                return []

            # Try to extract pages if available
            try:
                # Docling's pages structure varies by version
                # Try different ways to access pages
                pages_dict = None
                if hasattr(doc_obj, 'pages'):
                    pages_attr = doc_obj.pages
                    # Pages might be a dict {page_num: page_obj} or a list
                    if isinstance(pages_attr, dict):
                        pages_dict = pages_attr
                    elif hasattr(pages_attr, 'items'):
                        pages_dict = dict(pages_attr.items())
                
                if pages_dict:
                    # Extract text from each page
                    for page_num, page_obj in sorted(pages_dict.items()):
                        try:
                            # Try to get text from page object
                            if hasattr(page_obj, 'export_to_markdown'):
                                page_text = page_obj.export_to_markdown()
                            elif hasattr(page_obj, 'text'):
                                page_text = page_obj.text
                            elif isinstance(page_obj, dict):
                                page_text = page_obj.get('text') or page_obj.get('content') or str(page_obj)
                            else:
                                # Skip if we can't get text
                                continue
                            
                            if page_text and page_text.strip():
                                doc = Document(
                                    content=page_text.strip(),
                                    metadata={
                                        "filename": path.name,
                                        "file_path": str(path),
                                        "extraction_method": "docling",
                                        "has_tables": self._has_tables(page_text)
                                    },
                                    source=str(path),
                                    page_number=int(page_num) if isinstance(page_num, (int, str)) else None
                                )
                                documents.append(doc)
                        except Exception as e:
                            logger.warning(f"Failed to extract page {page_num}: {e}")
                            continue
                
                # If we didn't get pages, use the full text
                if not documents and full_text.strip():
                    doc = Document(
                        content=full_text.strip(),
                        metadata={
                            "filename": path.name,
                            "file_path": str(path),
                            "extraction_method": "docling",
                            "has_tables": self._has_tables(full_text)
                        },
                        source=str(path),
                        page_number=None
                    )
                    documents.append(doc)
                    
            except Exception as e:
                logger.warning(f"Failed to extract pages, using full text: {e}")
                # Fallback: use full text as single document
                if full_text.strip():
                    doc = Document(
                        content=full_text.strip(),
                        metadata={
                            "filename": path.name,
                            "file_path": str(path),
                            "extraction_method": "docling",
                            "has_tables": self._has_tables(full_text)
                        },
                        source=str(path),
                        page_number=None
                    )
                    documents.append(doc)
            
            if documents:
                logger.info(f"✓ Extracted {len(documents)} page(s) from {path.name}")
            else:
                logger.warning(f"No documents extracted from {path.name}")
            
            return documents
            
        except Exception as e:
            logger.error(f"✗ Error extracting {file_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _has_tables(self, text: str) -> bool:
        """Check if text contains markdown tables."""
        lines = text.split('\n')
        for line in lines:
            if '|' in line and line.count('|') >= 2:
                return True
        return False