"""Main script for running the customer support document pipeline."""

import argparse
import logging
from pathlib import Path

from config.config import Config
from src.load_data import CustomerSupportPipeline, SearchPipeline, setup_logging


def main():
    """Main entry point for the pipeline."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Customer Support Document Processing Pipeline"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process documents")
    process_parser.add_argument(
        "path",
        type=str,
        help="Path to PDF file or directory containing PDFs"
    )
    process_parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (optional)"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    search_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    search_parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Minimum similarity score threshold (0-1)"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get collection info")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Setup logging
    log_file = Path(args.log_file) if hasattr(args, "log_file") and args.log_file else None
    setup_logging(log_file)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = Config.from_env()
        logger.info("Configuration loaded successfully")
        
        if args.command == "process":
            # Process documents
            path = Path(args.path)
            
            if not path.exists():
                logger.error(f"Path does not exist: {path}")
                return
            
            pipeline = CustomerSupportPipeline(config)
            
            if path.is_file():
                logger.info(f"Processing single file: {path}")
                stats = pipeline.process_file(path)
            elif path.is_dir():
                logger.info(f"Processing directory: {path}")
                stats = pipeline.process_directory(path)
            else:
                logger.error(f"Invalid path: {path}")
                return
            
            # Print summary
            print("\n" + "=" * 60)
            print("PIPELINE SUMMARY")
            print("=" * 60)
            print(f"Documents processed: {stats['documents_processed']}")
            print(f"Documents failed: {stats['documents_failed']}")
            print(f"Total chunks created: {stats['total_chunks']}")
            print(f"Chunks embedded: {stats['chunks_embedded']}")
            print(f"Chunks stored: {stats['chunks_stored']}")
            print("=" * 60)
            
        elif args.command == "search":
            # Search documents
            search_pipeline = SearchPipeline(config)
            
            results = search_pipeline.search(
                query=args.query,
                top_k=args.top_k,
                score_threshold=args.threshold
            )
            
            # Print results
            print("\n" + "=" * 60)
            print(f"SEARCH RESULTS FOR: {args.query}")
            print("=" * 60)
            
            if not results:
                print("No results found.")
            else:
                for i, result in enumerate(results, 1):
                    print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
                    print(f"Source: {result['source_filename']}")
                    print(f"Chunk: {result['chunk_index']}")
                    print(f"Text: {result['text'][:300]}...")
                    print("-" * 60)
            
        elif args.command == "info":
            # Get collection info
            pipeline = CustomerSupportPipeline(config)
            info = pipeline.get_database_info()
            
            print("\n" + "=" * 60)
            print("COLLECTION INFORMATION")
            print("=" * 60)
            print(f"Collection name: {info.get('name', 'N/A')}")
            print(f"Total points: {info.get('points_count', 0)}")
            print(f"Vectors count: {info.get('vectors_count', 0)}")
            print(f"Vector size: {info.get('vector_size', 0)}")
            print(f"Status: {info.get('status', 'N/A')}")
            print("=" * 60)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nError: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nUnexpected error: {e}")
        print("Check the log file for more details.")


if __name__ == "__main__":
    main()
