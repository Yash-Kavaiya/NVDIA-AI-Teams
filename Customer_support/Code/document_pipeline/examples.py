"""
Example usage and integration tests for the document pipeline.
Demonstrates the power of SOLID principles and dependency injection.
"""
import asyncio
import logging
from config import Config
from extractor import DoclingExtractor
from chunker import OverlapTextChunker
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker
from retrieval_pipeline import RetrievalPipeline
from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_1_process_single_pdf():
    """Example: Process a single PDF file."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Process Single PDF")
    print("="*80 + "\n")
    
    config = Config.from_env()
    config.validate()
    
    # Create components
    extractor = DoclingExtractor()
    chunker = OverlapTextChunker(config.processing)
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    
    # Process single file
    processor = DocumentProcessor(extractor, chunker, embedder, vector_db)
    stats = await processor.process_single_file(
        "../Data/RegulatedProductsHandbook.pdf"
    )
    
    print(f"\nProcessing Stats:")
    print(f"  Success: {stats['success']}")
    print(f"  Chunks: {stats['chunks']}")
    print(f"  Embeddings: {stats['embeddings']}")


async def example_2_basic_search():
    """Example: Basic search without reranking."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Basic Search (No Reranking)")
    print("="*80 + "\n")
    
    config = Config.from_env()
    
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    
    query = "What are the retail compliance requirements?"
    print(f"Query: {query}\n")
    
    # Search without reranking (faster but less precise)
    results = await retrieval.retrieve(query, top_k=5, use_reranking=False)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result.score:.4f}")
        print(f"   {result.content[:100]}...\n")


async def example_3_search_with_reranking():
    """Example: Search with reranking for better results."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Search with Reranking (Better Results)")
    print("="*80 + "\n")
    
    config = Config.from_env()
    
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    
    query = "What are the environmental compliance standards?"
    print(f"Query: {query}\n")
    
    # Search with reranking (slower but more precise)
    results = await retrieval.retrieve(query, top_k=5, use_reranking=True)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result.score:.4f}")
        print(f"   Source: {result.source}")
        if result.page_number:
            print(f"   Page: {result.page_number}")
        print(f"   {result.content[:150]}...\n")


async def example_4_compare_reranking():
    """Example: Compare results with and without reranking."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Compare Reranking Impact")
    print("="*80 + "\n")
    
    config = Config.from_env()
    
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    
    query = "retail product labeling requirements"
    print(f"Query: {query}\n")
    
    # Without reranking
    print("WITHOUT RERANKING:")
    results_no_rerank = await retrieval.retrieve(query, top_k=3, use_reranking=False)
    for i, result in enumerate(results_no_rerank, 1):
        print(f"  {i}. [{result.score:.3f}] {result.content[:80]}...")
    
    print("\nWITH RERANKING:")
    results_rerank = await retrieval.retrieve(query, top_k=3, use_reranking=True)
    for i, result in enumerate(results_rerank, 1):
        print(f"  {i}. [{result.score:.3f}] {result.content[:80]}...")
    
    print("\nNotice how reranking can change the order and relevance!")


async def example_5_batch_queries():
    """Example: Process multiple queries efficiently."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Batch Queries")
    print("="*80 + "\n")
    
    config = Config.from_env()
    
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    
    queries = [
        "product safety regulations",
        "retail environmental standards",
        "compliance documentation requirements"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = await retrieval.retrieve(query, top_k=2, use_reranking=True)
        print(f"Found {len(results)} results")
        if results:
            print(f"  Top result: {results[0].content[:80]}...")


async def example_6_rag_context():
    """Example: Get results formatted for RAG (Retrieval Augmented Generation)."""
    print("\n" + "="*80)
    print("EXAMPLE 6: RAG-Ready Context")
    print("="*80 + "\n")
    
    config = Config.from_env()
    
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    
    query = "What are the key retail compliance areas?"
    print(f"Query: {query}\n")
    
    # Get results with full context
    response = await retrieval.retrieve_with_context(
        query=query,
        top_k=3,
        use_reranking=True
    )
    
    print("RAG Context:")
    print(f"  Query: {response['query']}")
    print(f"  Results Count: {response['results_count']}")
    print(f"  Reranked: {response['reranked']}")
    print("\nTop Results:")
    
    for i, result in enumerate(response['results'], 1):
        print(f"\n{i}. Score: {result['score']:.4f}")
        print(f"   Source: {result['source']}")
        if result['page_number']:
            print(f"   Page: {result['page_number']}")
        print(f"   Content: {result['content'][:200]}...")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("DOCUMENT PIPELINE EXAMPLES")
    print("="*80)
    
    # Note: Uncomment the examples you want to run
    
    # Example 1: Process a single PDF
    # asyncio.run(example_1_process_single_pdf())
    
    # Example 2: Basic search
    # asyncio.run(example_2_basic_search())
    
    # Example 3: Search with reranking
    asyncio.run(example_3_search_with_reranking())
    
    # Example 4: Compare reranking
    # asyncio.run(example_4_compare_reranking())
    
    # Example 5: Batch queries
    # asyncio.run(example_5_batch_queries())
    
    # Example 6: RAG context
    # asyncio.run(example_6_rag_context())


if __name__ == "__main__":
    main()
