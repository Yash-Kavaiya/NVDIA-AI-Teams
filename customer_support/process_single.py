"""Process a single PDF document with timeout handling."""

import sys
import logging
from pathlib import Path

from config.config import Config
from src.load_data import CustomerSupportPipeline, setup_logging


def main():
    """Process a single PDF file."""
    
    if len(sys.argv) != 2:
        print("Usage: python process_single.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"Error: Not a PDF file: {pdf_path}")
        sys.exit(1)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = Config.from_env()
        logger.info("Configuration loaded successfully")
        
        # Initialize pipeline
        pipeline = CustomerSupportPipeline(config)
        logger.info(f"Processing file: {pdf_path.name}")
        
        # Process the file
        stats = pipeline.process_file(pdf_path)
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"FILE: {pdf_path.name}")
        print("=" * 60)
        print(f"Status: {'SUCCESS' if stats['documents_processed'] > 0 else 'FAILED'}")
        print(f"Chunks created: {stats['total_chunks']}")
        print(f"Chunks embedded: {stats['chunks_embedded']}")
        print(f"Chunks stored: {stats['chunks_stored']}")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
