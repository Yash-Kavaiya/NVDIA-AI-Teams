"""
Test script for Product Search Agent

This script tests the functionality of the product search agent tools
to ensure they work correctly with the NVIDIA embeddings and Qdrant.
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
agent_path = Path(__file__).parent.parent.parent.parent / "image_embeddings_pipeline"
sys.path.insert(0, str(agent_path))

def test_environment():
    """Test that environment is properly configured."""
    print("=" * 60)
    print("Testing Environment Configuration")
    print("=" * 60)
    
    from config.config import Config
    
    try:
        config = Config.from_env()
        config.validate()
        print("✓ Configuration loaded successfully")
        print(f"  - NVIDIA API URL: {config.nvidia.embedding_url}")
        print(f"  - Qdrant URL: {config.qdrant.url}")
        print(f"  - Collection: {config.qdrant.collection_name}")
        print(f"  - Embedding Dimension: {config.qdrant.embedding_dim}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_qdrant_connection():
    """Test connection to Qdrant database."""
    print("\n" + "=" * 60)
    print("Testing Qdrant Connection")
    print("=" * 60)
    
    from qdrant_client import QdrantClient
    from config.config import Config
    
    try:
        config = Config.from_env()
        client = QdrantClient(url=config.qdrant.url)
        
        # Check if collection exists
        collections = client.get_collections()
        print(f"✓ Connected to Qdrant at {config.qdrant.url}")
        print(f"  - Available collections: {[c.name for c in collections.collections]}")
        
        if config.qdrant.collection_name in [c.name for c in collections.collections]:
            info = client.get_collection(config.qdrant.collection_name)
            print(f"✓ Collection '{config.qdrant.collection_name}' exists")
            print(f"  - Total points: {info.points_count}")
            print(f"  - Indexed vectors: {info.indexed_vectors_count}")
            return True
        else:
            print(f"⚠ Collection '{config.qdrant.collection_name}' not found")
            print("  Run the indexing pipeline first: cd image_embeddings_pipeline && python main.py")
            return False
            
    except Exception as e:
        print(f"✗ Qdrant connection error: {e}")
        return False


def test_text_search():
    """Test text-to-image search functionality."""
    print("\n" + "=" * 60)
    print("Testing Text-to-Image Search")
    print("=" * 60)
    
    from product_search_agent import tools
    
    try:
        # Test basic text search
        print("\nSearching for 'red dress'...")
        results = tools.search_products_by_text(
            query="red dress",
            limit=5,
            score_threshold=0.0
        )
        
        if "error" in results:
            print(f"✗ Search error: {results['error']}")
            return False
        
        print(f"✓ Search completed successfully")
        print(f"  - Query: {results['query']}")
        print(f"  - Results found: {results['results_count']}")
        
        if results['results_count'] > 0:
            print("\n  Top 3 Results:")
            for i, result in enumerate(results['results'][:3], 1):
                print(f"    {i}. {result['filename']}")
                print(f"       Score: {result['similarity_score']}")
                print(f"       URL: {result['image_url'][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Text search error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_collection_stats():
    """Test collection statistics retrieval."""
    print("\n" + "=" * 60)
    print("Testing Collection Statistics")
    print("=" * 60)
    
    from product_search_agent import tools
    
    try:
        stats = tools.get_collection_stats()
        
        if "error" in stats:
            print(f"✗ Stats error: {stats['error']}")
            return False
        
        print("✓ Collection statistics retrieved successfully")
        print(f"  - Collection: {stats['collection_name']}")
        print(f"  - Total products: {stats['total_products']}")
        print(f"  - Indexed vectors: {stats['indexed_vectors']}")
        print(f"  - Status: {stats['collection_status']}")
        print(f"  - All indexed: {stats['health']['all_vectors_indexed']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Collection stats error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_search():
    """Test image-to-image search functionality."""
    print("\n" + "=" * 60)
    print("Testing Image-to-Image Search")
    print("=" * 60)
    
    from product_search_agent import tools
    
    # Use a sample image URL from the dataset
    sample_url = "http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg"
    
    try:
        print(f"\nSearching for similar images to:\n  {sample_url}")
        results = tools.search_products_by_image(
            image_url=sample_url,
            limit=5,
            score_threshold=0.0
        )
        
        if "error" in results:
            print(f"✗ Image search error: {results['error']}")
            return False
        
        print(f"✓ Image search completed successfully")
        print(f"  - Results found: {results['results_count']}")
        
        if results['results_count'] > 0:
            print("\n  Top 3 Similar Products:")
            for i, result in enumerate(results['results'][:3], 1):
                print(f"    {i}. {result['filename']}")
                print(f"       Similarity: {result['similarity_score']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Image search error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("PRODUCT SEARCH AGENT - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Qdrant Connection", test_qdrant_connection),
        ("Collection Statistics", test_collection_stats),
        ("Text Search", test_text_search),
        ("Image Search", test_image_search),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The Product Search Agent is ready to use.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    run_all_tests()
