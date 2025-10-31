"""
Main entry point for document processing and retrieval.
Demonstrates dependency injection and composition of SOLID components.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/document_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from config import Config
from extractor import DoclingExtractor
from chunker import OverlapTextChunker
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker
from retrieval_pipeline import RetrievalPipeline
from document_processor import DocumentProcessor


async def process_documents(config: Config, data_dir: str):
    """
    Process all PDFs in a directory.
    
    This function demonstrates the composition of components
    following SOLID principles and dependency injection.
    """
    logger.info("="*80)
    logger.info("DOCUMENT PROCESSING PIPELINE")
    logger.info("="*80)
    
    # Create component instances (dependency injection)
    extractor = DoclingExtractor()
    chunker = OverlapTextChunker(config.processing)
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    
    # Create document processor (facade pattern)
    processor = DocumentProcessor(
        extractor=extractor,
        chunker=chunker,
        embedder=embedder,
        vector_db=vector_db
    )
    
    # Process directory
    stats = await processor.process_directory(data_dir)
    
    return stats


async def search_documents(config: Config, query: str, top_k: int = 10):
    """
    Search processed documents.
    
    Demonstrates the retrieval pipeline with reranking.
    """
    logger.info("="*80)
    logger.info("DOCUMENT RETRIEVAL")
    logger.info("="*80)
    
    # Create component instances
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    # Create retrieval pipeline
    retrieval = RetrievalPipeline(
        embedder=embedder,
        vector_db=vector_db,
        reranker=reranker,
        config=config.retrieval
    )
    
    # Perform search
    logger.info(f"Query: {query}")
    results = await retrieval.retrieve(
        query=query,
        top_k=top_k,
        use_reranking=True
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"SEARCH RESULTS (Top {len(results)})")
    print("="*80 + "\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Score: {result.score:.4f}")
        print(f"  Source: {result.source}")
        if result.page_number:
            print(f"  Page: {result.page_number}")
        print(f"  Content: {result.content[:200]}...")
        print()
    
    return results


async def interactive_search(config: Config):
    """Interactive search mode."""
    logger.info("="*80)
    logger.info("INTERACTIVE SEARCH MODE")
    logger.info("="*80)
    
    # Create components
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    # Create retrieval pipeline
    retrieval = RetrievalPipeline(
        embedder=embedder,
        vector_db=vector_db,
        reranker=reranker,
        config=config.retrieval
    )
    
    # Get collection info
    info = vector_db.get_collection_info()
    print(f"\nCollection: {info.get('name')}")
    print(f"Documents: {info.get('points_count', 0)}")
    print(f"\nEnter your search queries (type 'quit' to exit):\n")
    
    while True:
        try:
            query = input("Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            print("\nSearching...")
            results = await retrieval.retrieve(
                query=query,
                use_reranking=True
            )
            
            if not results:
                print("No results found.\n")
                continue
            
            print(f"\nFound {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result.score:.3f}] {result.source}")
                if result.page_number:
                    print(f"   Page {result.page_number}")
                print(f"   {result.content[:150]}...\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def main():
    """Main entry point."""
    # Load and validate configuration
    config = Config.from_env()
    
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set required environment variables in .env file")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Process documents: python main.py process <directory>")
        print("  Search documents:  python main.py search <query>")
        print("  Interactive mode:  python main.py interactive")
        print("\nExample:")
        print("  python main.py process ../Data")
        print("  python main.py search 'retail compliance requirements'")
        print("  python main.py interactive")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "process":
        if len(sys.argv) < 3:
            print("Error: Please specify directory path")
            print("Example: python main.py process ../Data")
            sys.exit(1)
        
        data_dir = sys.argv[2]
        asyncio.run(process_documents(config, data_dir))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please specify search query")
            print("Example: python main.py search 'retail compliance'")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        asyncio.run(search_documents(config, query))
    
    elif command == "interactive":
        asyncio.run(interactive_search(config))
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: process, search, interactive")
        sys.exit(1)


if __name__ == "__main__":
    main()
