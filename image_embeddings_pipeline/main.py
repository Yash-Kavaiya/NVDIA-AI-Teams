"""Main entry point."""
import asyncio
import logging
import sys
from pathlib import Path

from config.config import Config
from src.pipeline import ImageEmbeddingPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function."""
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        
        # Parse command line arguments
        start_from = int(sys.argv[1]) if len(sys.argv) > 1 else 0
        max_images = int(sys.argv[2]) if len(sys.argv) > 2 else None
        csv_file = sys.argv[3] if len(sys.argv) > 3 else "data/images.csv"
        
        if not Path(csv_file).exists():
            logger.error(f"CSV file not found: {csv_file}")
            return
        
        # Print mode
        if start_from > 0 or max_images:
            print(f"Mode: Resume/Limited processing")
            if start_from > 0:
                print(f"  Start from row: {start_from}")
            if max_images:
                print(f"  Max images: {max_images}")
            print()
        
        # Create and run pipeline
        pipeline = ImageEmbeddingPipeline(config)
        success, failure = await pipeline.process_csv(csv_file, start_from, max_images)
        
        logger.info(f"Pipeline completed: {success} success, {failure} failures")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        print("You can resume by running: python main.py <last_row_processed>")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())