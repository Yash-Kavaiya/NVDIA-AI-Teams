"""
Interactive search CLI for the document pipeline.
Run this to search the ingested documents interactively.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker
from retrieval_pipeline import RetrievalPipeline
import logging

# Simple console logging
logging.basicConfig(level=logging.WARNING)

def print_result(result, index):
    """Print a search result."""
    print(f"\n{'─'*80}")
    print(f"Result #{index}  |  Score: {result.score:.4f}  |  Rank: {result.rank}")
    print(f"{'─'*80}")
    
    # Metadata
    metadata = result.document.metadata
    if 'source' in metadata:
        print(f"📄 Source: {metadata['source']}")
    if 'chunk_index' in metadata:
        print(f"📝 Chunk: {metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}")
    
    # Content
    print(f"\n{result.document.content}\n")

def search_interactive(retrieval_pipeline):
    """Interactive search loop."""
    print("\n" + "="*80)
    print("  CPSC Document Search - Interactive Mode")
    print("="*80)
    print("\nCommands:")
    print("  • Type your query and press Enter")
    print("  • Type 'quit' or 'exit' to stop")
    print("  • Type 'help' for sample queries")
    print("="*80 + "\n")
    
    while True:
        try:
            # Get query
            query = input("🔍 Search> ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n📚 Sample queries:")
                print("  • What is the Consumer Product Safety Commission?")
                print("  • When was CPSC established?")
                print("  • What products does CPSC regulate?")
                print("  • How does CPSC enforce regulations?")
                print("  • What are the seven statutes CPSC administers?")
                continue
            
            # Perform search
            print("\n⏳ Searching...")
            results = retrieval_pipeline.search(query)
            
            # Display results
            if not results:
                print("\n❌ No results found. Try a different query.")
                continue
            
            print(f"\n✓ Found {len(results)} result(s):\n")
            
            for i, result in enumerate(results, 1):
                print_result(result, i)
            
            print("="*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

def main():
    """Main function."""
    print("Initializing search system...")
    
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        
        # Initialize components
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
            print("\n❌ Error: Collection not found!")
            print("\nPlease run ingestion first:")
            print("  python main.py")
            return
        
        reranker = NvidiaReranker(
            api_key=config.nvidia.api_key,
            model=config.nvidia.reranker_model
        )
        
        retrieval_pipeline = RetrievalPipeline(
            embedding_generator=embedding_generator,
            vector_db=vector_db,
            reranker=reranker,
            config=config.retrieval
        )
        
        print("✓ System ready!\n")
        
        # Start interactive search
        search_interactive(retrieval_pipeline)
        
    except Exception as e:
        print(f"\n❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
