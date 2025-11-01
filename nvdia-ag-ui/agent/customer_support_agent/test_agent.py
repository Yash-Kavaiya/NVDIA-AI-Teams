"""
Test script for Customer Support Agent

Tests the tools and agent functionality for retail policy search.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "customer_support"))

from customer_support_agent.tools import (
    search_policy_documents,
    get_collection_info,
    CustomerSupportTools
)


async def test_search_policy_documents():
    """Test searching policy documents."""
    print("\n" + "="*60)
    print("TEST: Search Policy Documents")
    print("="*60)
    
    test_queries = [
        "What is the return policy for electronics?",
        "Can I get a refund without a receipt?",
        "What is the warranty period?",
        "Do you accept returns on sale items?",
        "What are the shipping options?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 60)
        
        result = search_policy_documents(query=query, top_k=3)
        
        if result["success"]:
            print(f"✅ Found {result['results_count']} results")
            print(f"   Reranking applied: {result.get('reranking_applied', 'N/A')}")
            
            for i, doc in enumerate(result["results"], 1):
                print(f"\n   Result #{i}:")
                print(f"   📄 Source: {doc['source_filename']}")
                print(f"   📍 Chunk: {doc['chunk_index']}")
                print(f"   📊 Similarity: {doc['similarity_score']:.4f}")
                if doc['rerank_score'] is not None:
                    print(f"   🎯 Rerank Score: {doc['rerank_score']:.4f}")
                print(f"   📝 Text Preview: {doc['text'][:150]}...")
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            print(f"   Message: {result.get('message', '')}")


def test_get_collection_info():
    """Test getting collection information."""
    print("\n" + "="*60)
    print("TEST: Get Collection Info")
    print("="*60)
    
    result = get_collection_info()
    
    if result["success"]:
        print("✅ Collection Information:")
        print(f"   📦 Collection Name: {result['collection_name']}")
        print(f"   📊 Total Chunks: {result['total_chunks']}")
        print(f"   🔢 Vectors Count: {result.get('vectors_count', 'N/A')}")
        print(f"   ✅ Status: {result['status']}")
        print(f"   📏 Vector Size: {result['vector_size']}")
        print(f"   ⚙️ Optimizer Status: {result.get('optimizer_status', 'N/A')}")
    else:
        print(f"❌ Failed to get collection info: {result.get('error', 'Unknown error')}")
        print(f"   Message: {result.get('message', '')}")


async def test_advanced_search():
    """Test advanced search scenarios."""
    print("\n" + "="*60)
    print("TEST: Advanced Search Scenarios")
    print("="*60)
    
    tools = CustomerSupportTools()
    
    # Test with reranking
    print("\n🔍 Test 1: With Reranking (default)")
    result1 = await tools.search_policy_documents(
        query="electronics return policy",
        top_k=5,
        use_reranking=True
    )
    print(f"   Results: {result1['results_count']}")
    
    # Test without reranking
    print("\n🔍 Test 2: Without Reranking")
    result2 = await tools.search_policy_documents(
        query="electronics return policy",
        top_k=5,
        use_reranking=False
    )
    print(f"   Results: {result2['results_count']}")
    
    # Test with score threshold
    print("\n🔍 Test 3: With Score Threshold (0.7)")
    result3 = await tools.search_policy_documents(
        query="warranty information",
        top_k=10,
        use_reranking=True,
        score_threshold=0.7
    )
    print(f"   Results: {result3['results_count']}")
    
    # Test with ambiguous query
    print("\n🔍 Test 4: Ambiguous Query")
    result4 = await tools.search_policy_documents(
        query="xyz abc def",
        top_k=3,
        use_reranking=True
    )
    print(f"   Results: {result4['results_count']}")
    if result4['results_count'] == 0:
        print(f"   Message: {result4['message']}")
    
    await tools.close()


def test_error_handling():
    """Test error handling."""
    print("\n" + "="*60)
    print("TEST: Error Handling")
    print("="*60)
    
    # Test with empty query
    print("\n🔍 Test 1: Empty Query")
    result1 = search_policy_documents(query="", top_k=3)
    print(f"   Success: {result1['success']}")
    print(f"   Results: {result1['results_count']}")
    
    # Test with very long query
    print("\n🔍 Test 2: Very Long Query")
    long_query = "return policy " * 1000  # Very long query
    result2 = search_policy_documents(query=long_query, top_k=3)
    print(f"   Success: {result2['success']}")
    print(f"   Results: {result2['results_count']}")
    
    # Test with top_k = 0
    print("\n🔍 Test 3: Invalid top_k")
    result3 = search_policy_documents(query="return policy", top_k=0)
    print(f"   Success: {result3['success']}")
    print(f"   Results: {result3['results_count']}")


def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("""
✅ All tests completed!

What was tested:
1. Basic policy document search
2. Collection information retrieval
3. Advanced search scenarios (reranking, thresholds)
4. Error handling and edge cases

Next steps:
1. Verify results match expected policy content
2. Test agent integration in UI (npm run dev)
3. Check response quality and citations
4. Monitor performance with large document sets

To test the full agent:
1. Start the app: cd nvdia-ag-ui && npm run dev
2. Navigate to: http://localhost:3000
3. Select: Customer Support Agent
4. Ask policy questions and verify:
   - Accurate answers with citations
   - Proper source document references
   - Confidence scores displayed
   - Helpful suggestions when no results
    """)


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CUSTOMER SUPPORT AGENT - TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Collection info
        test_get_collection_info()
        
        # Test 2: Search policy documents
        await test_search_policy_documents()
        
        # Test 3: Advanced search
        await test_advanced_search()
        
        # Test 4: Error handling
        test_error_handling()
        
        # Print summary
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
