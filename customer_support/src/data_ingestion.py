"""Data ingestion module using Docling for PDF processing."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.document import DoclingDocument

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    
    filename: str
    filepath: str
    total_pages: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class PDFProcessor:
    """Handles PDF document extraction using Docling.
    
    Single Responsibility: Extract and parse PDF documents.
    """
    
    def __init__(self, generate_page_images: bool = False):
        """Initialize PDF processor with Docling converter.
        
        Args:
            generate_page_images: If True, generates page images for better HTML previews
        """
        self.generate_page_images = generate_page_images
        self.converter = self._create_converter()
        logger.info("PDFProcessor initialized with Docling backend")
    
    def _create_converter(self) -> DocumentConverter:
        """Create and configure DocumentConverter.
        
        Returns:
            Configured DocumentConverter instance
        """
        pipeline_options = PdfPipelineOptions()
        pipeline_options.generate_page_images = self.generate_page_images
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    backend=DoclingParseV4DocumentBackend
                )
            }
        )
        
        return converter
    
    def process_pdf(self, pdf_path: Path) -> tuple[Optional[DoclingDocument], DocumentMetadata]:
        """Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (DoclingDocument or None, DocumentMetadata)
        """
        import time
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing PDF: {pdf_path.name}")
            
            # Convert the document
            result = self.converter.convert(pdf_path)
            
            processing_time = time.time() - start_time
            
            if result.document is None:
                metadata = DocumentMetadata(
                    filename=pdf_path.name,
                    filepath=str(pdf_path),
                    total_pages=0,
                    processing_time=processing_time,
                    success=False,
                    error_message="Document conversion returned None"
                )
                logger.error(f"Failed to convert {pdf_path.name}")
                return None, metadata
            
            # Extract page count
            page_count = len(list(result.document.pages))
            
            metadata = DocumentMetadata(
                filename=pdf_path.name,
                filepath=str(pdf_path),
                total_pages=page_count,
                processing_time=processing_time,
                success=True
            )
            
            logger.info(
                f"Successfully processed {pdf_path.name}: "
                f"{page_count} pages in {processing_time:.2f}s"
            )
            
            return result.document, metadata
            
        except Exception as e:
            processing_time = time.time() - start_time
            metadata = DocumentMetadata(
                filename=pdf_path.name,
                filepath=str(pdf_path),
                total_pages=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
            logger.error(f"Error processing {pdf_path.name}: {e}", exc_info=True)
            return None, metadata
    
    def process_directory(
        self, 
        directory_path: Path,
        pattern: str = "*.pdf"
    ) -> List[tuple[Optional[DoclingDocument], DocumentMetadata]]:
        """Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            pattern: Glob pattern for matching files (default: *.pdf)
            
        Returns:
            List of tuples (DoclingDocument or None, DocumentMetadata)
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        pdf_files = list(directory_path.glob(pattern))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_path in pdf_files:
            doc, metadata = self.process_pdf(pdf_path)
            results.append((doc, metadata))
        
        # Log summary
        successful = sum(1 for _, m in results if m.success)
        failed = len(results) - successful
        
        logger.info(
            f"Processing complete: {successful} succeeded, {failed} failed"
        )
        
        return results


class DocumentExtractor:
    """High-level interface for document extraction.
    
    Single Responsibility: Coordinate PDF processing and extract structured content.
    """
    
    def __init__(self, pdf_processor: PDFProcessor):
        """Initialize with a PDF processor.
        
        Args:
            pdf_processor: PDFProcessor instance (Dependency Injection)
        """
        self.pdf_processor = pdf_processor
        logger.info("DocumentExtractor initialized")
    
    def extract_from_directory(
        self, 
        directory_path: Path,
        pattern: str = "*.pdf"
    ) -> List[Dict[str, Any]]:
        """Extract structured content from all PDFs in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            pattern: Glob pattern for matching files
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        results = self.pdf_processor.process_directory(directory_path, pattern)
        
        extracted_data = []
        
        for doc, metadata in results:
            if doc is None or not metadata.success:
                # Still include failed documents in output for tracking
                extracted_data.append({
                    "document": None,
                    "content": "",
                    "metadata": {
                        "filename": metadata.filename,
                        "filepath": metadata.filepath,
                        "total_pages": metadata.total_pages,
                        "processing_time": metadata.processing_time,
                        "success": metadata.success,
                        "error_message": metadata.error_message
                    }
                })
                continue
            
            # Extract full text from document
            full_text = doc.export_to_markdown()
            
            extracted_data.append({
                "document": doc,  # Keep original DoclingDocument for chunking
                "content": full_text,
                "metadata": {
                    "filename": metadata.filename,
                    "filepath": metadata.filepath,
                    "total_pages": metadata.total_pages,
                    "processing_time": metadata.processing_time,
                    "success": metadata.success
                }
            })
        
        logger.info(f"Extracted content from {len(extracted_data)} documents")
        
        return extracted_data
    
    def extract_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract structured content from a single PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing document content and metadata
        """
        doc, metadata = self.pdf_processor.process_pdf(file_path)
        
        if doc is None or not metadata.success:
            return {
                "document": None,
                "content": "",
                "metadata": {
                    "filename": metadata.filename,
                    "filepath": metadata.filepath,
                    "total_pages": metadata.total_pages,
                    "processing_time": metadata.processing_time,
                    "success": metadata.success,
                    "error_message": metadata.error_message
                }
            }
        
        # Extract full text from document
        full_text = doc.export_to_markdown()
        
        return {
            "document": doc,
            "content": full_text,
            "metadata": {
                "filename": metadata.filename,
                "filepath": metadata.filepath,
                "total_pages": metadata.total_pages,
                "processing_time": metadata.processing_time,
                "success": metadata.success
            }
        }
