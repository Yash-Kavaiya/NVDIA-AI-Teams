"""Test script for document search functionality."""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker
from retrieval_pipeline import RetrievalPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Test queries based on CPSC text
TEST_QUERIES = [
    "What is the Consumer Product Safety Commission?",
    "When was CPSC established?",
    "What are the main responsibilities of the CPSC?",
    "How many statutes does CPSC administer?",
    "What types of consumer products does CPSC regulate?",
    "What is the mission of the CPSC?",
    "How does CPSC achieve its goals?",
    "Is CPSC an independent federal agency?",
]

def test_search(query: str, pipeline: RetrievalPipeline):
    """
    Test a single search query.
    
    Args:
        query: Search query
        pipeline: Retrieval pipeline instance
    """
    logger.info("=" * 100)
    logger.info(f"QUERY: {query}")
    logger.info("=" * 100)
    
    try:
        results = pipeline.search(query)
        
        if not results:
            logger.warning("No results found")
            return
        
        logger.info(f"Found {len(results)} results:\n")
        
        for result in results:
            logger.info(f"Rank {result.rank} | Score: {result.score:.4f}")
            logger.info(f"Source: {result.document.metadata.get('source', 'Unknown')}")
            logger.info(f"Chunk: {result.document.metadata.get('chunk_index', 'N/A')}/{result.document.metadata.get('total_chunks', 'N/A')}")
            logger.info(f"Content:\n{result.document.content}\n")
            logger.info("-" * 100)
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)

def test_batch_search(queries: list, pipeline: RetrievalPipeline):
    """
    Test multiple queries and show summary.
    
    Args:
        queries: List of search queries
        pipeline: Retrieval pipeline instance
    """
    logger.info("\n" + "=" * 100)
    logger.info("BATCH SEARCH TEST")
    logger.info("=" * 100 + "\n")
    
    results_summary = []
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n[{i}/{len(queries)}] Testing: {query}")
        
        try:
            results = pipeline.search(query)
            results_summary.append({
                "query": query,
                "num_results": len(results),
                "top_score": results[0].score if results else 0.0
            })
            
            if results:
                logger.info(f"✓ Found {len(results)} results (top score: {results[0].score:.4f})")
            else:
                logger.warning(f"✗ No results found")
                
        except Exception as e:
            logger.error(f"✗ Query failed: {e}")
            results_summary.append({
                "query": query,
                "num_results": 0,
                "top_score": 0.0,
                "error": str(e)
            })
    
    # Print summary
    logger.info("\n" + "=" * 100)
    logger.info("SUMMARY")
    logger.info("=" * 100)
    
    for item in results_summary:
        status = "✓" if item["num_results"] > 0 else "✗"
        logger.info(f"{status} {item['query'][:60]}: {item['num_results']} results (score: {item['top_score']:.4f})")
    
    total_queries = len(results_summary)
    successful = sum(1 for item in results_summary if item["num_results"] > 0)
    logger.info(f"\nSuccess rate: {successful}/{total_queries} ({successful/total_queries*100:.1f}%)")

def main():
    """Main test function."""
    logger.info("=" * 100)
    logger.info("DOCUMENT SEARCH TEST")
    logger.info("=" * 100)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config.from_env()
        config.validate()
        logger.info("✓ Configuration loaded")
        
        # Initialize components
        logger.info("Initializing components...")
        
        embedding_generator = NvidiaEmbeddingGenerator(
            api_key=config.nvidia.api_key,
            model=config.nvidia.embedding_model
        )
        
        vector_db = QdrantVectorDB(
            url=config.qdrant.url,
            collection_name=config.qdrant.collection_name,
            vector_size=config.qdrant.embedding_dim
        )
        
        # Check if collection exists
        if not vector_db.collection_exists():
            logger.error("Collection does not exist! Please run main.py first to ingest documents.")
            sys.exit(1)
        
        # Get collection info
        info = vector_db.get_collection_info()
        logger.info(f"✓ Collection '{config.qdrant.collection_name}' found")
        logger.info(f"  - Vectors: {info.get('vectors_count', 'N/A')}")
        logger.info(f"  - Points: {info.get('points_count', 'N/A')}")
        logger.info(f"  - Status: {info.get('status', 'N/A')}")
        
        reranker = NvidiaReranker(
            api_key=config.nvidia.api_key,
            model=config.nvidia.reranker_model
        )
        
        pipeline = RetrievalPipeline(
            embedding_generator=embedding_generator,
            vector_db=vector_db,
            reranker=reranker,
            config=config.retrieval
        )
        
        logger.info("✓ All components initialized\n")
        
        # Run tests
        # Test mode: single query or batch
        test_mode = input("Test mode [1=Single, 2=Batch, 3=Custom]: ").strip()
        
        if test_mode == "1":
            # Single query test
            query = TEST_QUERIES[0]
            test_search(query, pipeline)
            
        elif test_mode == "2":
            # Batch test
            test_batch_search(TEST_QUERIES, pipeline)
            
        elif test_mode == "3":
            # Custom query
            custom_query = input("Enter your query: ").strip()
            if custom_query:
                test_search(custom_query, pipeline)
            else:
                logger.warning("Empty query provided")
        else:
            logger.info("Invalid mode. Running default test...")
            test_search(TEST_QUERIES[0], pipeline)
        
        logger.info("\n" + "=" * 100)
        logger.info("TEST COMPLETE")
        logger.info("=" * 100)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
