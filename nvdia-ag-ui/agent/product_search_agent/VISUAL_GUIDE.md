# Product Search Agent - Visual Architecture Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (Next.js)                         │
│                      http://localhost:3000                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  CopilotKit Chat Interface                        │  │
│  │  User: "Find me red summer dresses"                              │  │
│  │  Agent: [Shows results with images and similarity scores]        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP/WebSocket
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RETAIL COORDINATOR AGENT                              │
│                    (Google ADK + Gemini 2.5 Flash)                      │
│                    http://localhost:8000                                │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Routes query to appropriate sub-agent based on intent           │  │
│  │ Query type: Product search → product_search_agent               │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Sub-agent invocation
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PRODUCT SEARCH AGENT                                │
│                    (Google ADK + Gemini 2.0 Flash)                      │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Agent Capabilities:                                              │  │
│  │ • Understands natural language queries                          │  │
│  │ • Selects appropriate tool (text/image/filtered search)        │  │
│  │ • Interprets similarity scores                                  │  │
│  │ • Formats results for user presentation                         │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                        TOOLS                                     │   │
│  │  1. search_products_by_text(query, limit, threshold)           │   │
│  │  2. search_products_by_image(url, limit, threshold)            │   │
│  │  3. search_with_filters(query, filters, limit)                 │   │
│  │  4. get_collection_stats()                                      │   │
│  │  5. get_product_by_id(id)                                       │   │
│  └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ Tool execution
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    IMAGE SEARCH ENGINE                                   │
│              (image_embeddings_pipeline/src/search_engine.py)           │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ async search_by_text():                                          │  │
│  │   1. Generate text embedding via NVIDIA API                     │  │
│  │   2. Query Qdrant for similar vectors                           │  │
│  │   3. Return ranked results                                      │  │
│  │                                                                  │  │
│  │ async search_by_image():                                        │  │
│  │   1. Download & encode image                                    │  │
│  │   2. Generate image embedding via NVIDIA API                    │  │
│  │   3. Query Qdrant for similar vectors                           │  │
│  │   4. Return ranked results                                      │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────┬───────────────────────────────────┬───────────────────────┘
              │                                   │
              ▼                                   ▼
┌─────────────────────────────┐    ┌──────────────────────────────────┐
│     NVIDIA NIM API          │    │      QDRANT VECTOR DB            │
│  integrate.api.nvidia.com   │    │   http://localhost:6333          │
│ ┌─────────────────────────┐ │    │ ┌──────────────────────────────┐ │
│ │ Model: nv-embed-v1      │ │    │ │ Collection: image_embeddings │ │
│ │ Type: Multimodal        │ │    │ │ Distance: COSINE             │ │
│ │ Dimensions: 4096        │ │    │ │ Vectors: 44,424 (indexed)    │ │
│ │ Parameters: 300M        │ │    │ │ Metadata: filename, url, etc │ │
│ │                         │ │    │ │                              │ │
│ │ Input:                  │ │    │ │ Operations:                  │ │
│ │ • Text query            │ │    │ │ • Vector search              │ │
│ │ • Image (base64)        │ │    │ │ • Metadata filtering         │ │
│ │                         │ │    │ │ • Point retrieval            │ │
│ │ Output:                 │ │    │ │                              │ │
│ │ • 4096-dim vector       │ │    │ │ Returns:                     │ │
│ │ • JSON format           │ │    │ │ • Scored points              │ │
│ │                         │ │    │ │ • Metadata payloads          │ │
│ └─────────────────────────┘ │    │ └──────────────────────────────┘ │
└─────────────────────────────┘    └──────────────────────────────────┘
```

## Data Structures

### Search Request Flow

```
TEXT SEARCH REQUEST
───────────────────
{
  "query": "red summer dress",
  "limit": 10,
  "score_threshold": 0.7
}
    │
    ▼
NVIDIA API REQUEST
──────────────────
{
  "input": ["red summer dress"],
  "model": "nvidia/nv-embed-v1",
  "encoding_format": "float",
  "input_type": "query"
}
    │
    ▼
NVIDIA API RESPONSE
───────────────────
{
  "data": [{
    "embedding": [0.123, -0.456, ..., 0.789],  // 4096 dimensions
    "index": 0
  }]
}
    │
    ▼
QDRANT SEARCH
─────────────
client.search(
  collection_name="image_embeddings",
  query_vector=[0.123, -0.456, ..., 0.789],
  limit=10,
  score_threshold=0.7
)
    │
    ▼
QDRANT RESULTS
──────────────
[
  {
    "id": 12345,
    "score": 0.8945,
    "payload": {
      "filename": "dress_001.jpg",
      "image_url": "http://...",
      "processed_at": "2024-01-15T10:30:00"
    }
  },
  ...
]
    │
    ▼
FORMATTED RESPONSE
──────────────────
{
  "query": "red summer dress",
  "results_count": 10,
  "results": [
    {
      "id": 12345,
      "filename": "dress_001.jpg",
      "image_url": "http://...",
      "similarity_score": 0.8945,
      "processed_at": "2024-01-15T10:30:00"
    },
    ...
  ]
}
```

### Image Search Request Flow

```
IMAGE SEARCH REQUEST
────────────────────
{
  "image_url": "http://example.com/shoe.jpg",
  "limit": 5,
  "score_threshold": 0.8
}
    │
    ▼
DOWNLOAD & ENCODE IMAGE
───────────────────────
1. Fetch image from URL
2. Resize to max 128x128 (configurable)
3. Convert to base64
4. Create data URI: "data:image/jpeg;base64,..."
    │
    ▼
NVIDIA API REQUEST
──────────────────
{
  "input": ["data:image/jpeg;base64,/9j/4AAQSkZJRg..."],
  "model": "nvidia/nv-embed-v1",
  "encoding_format": "float"
}
    │
    ▼
[Same flow as text search from here...]
```

## Vector Space Visualization

```
Semantic Vector Space (4096 dimensions, visualized in 2D)
──────────────────────────────────────────────────────────

                    Dresses
                      •
                  •       •
               •     •       •
            •          •        •
         Skirts    •      •   Evening Gowns
            •          •        •
               •     •       •
                  •       •
                    Pants
                      

         Shoes                         Watches
           •                              •
        •     •                        •     •
     •           •                  •           •
  Sneakers   Boots              Analog    Digital
     •           •                  •           •
        •     •                        •     •
           •                              •

                  Accessories
                      •
                  •       •
               •     •       •
            Bags      •      Jewelry
               •     •       •
                  •       •
```

**Key Insight**: Items that are semantically similar (e.g., "red dress" and "crimson gown") 
will have vectors close to each other in this high-dimensional space, even if the text 
doesn't exactly match!

## Search Algorithm

```
┌─────────────────────────────────────────────────────────────┐
│            COSINE SIMILARITY CALCULATION                     │
└─────────────────────────────────────────────────────────────┘

Given:
- Query vector Q = [q₁, q₂, ..., q₄₀₉₆]
- Product vector P = [p₁, p₂, ..., p₄₀₉₆]

Cosine Similarity = (Q · P) / (||Q|| × ||P||)

Where:
- Q · P = q₁p₁ + q₂p₂ + ... + q₄₀₉₆p₄₀₉₆  (dot product)
- ||Q|| = √(q₁² + q₂² + ... + q₄₀₉₆²)     (magnitude)

Result: Value between -1 and 1
- 1.0  = Identical vectors (perfect match)
- 0.9+ = Extremely similar
- 0.8  = Very similar
- 0.7  = Similar (recommended threshold)
- 0.0  = Orthogonal (unrelated)
```

## Performance Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  ASYNC CONCURRENT PROCESSING                    │
└────────────────────────────────────────────────────────────────┘

Single Request Timeline:
─────────────────────────

0ms    : Receive query
10ms   : Validate input
20ms   : Start async embedding generation
220ms  : Receive embedding from NVIDIA
230ms  : Start Qdrant search
240ms  : Receive results from Qdrant
250ms  : Format response
260ms  : Return to user

Total: ~260ms for text search
       ~560ms for image search (includes download)


Batch Processing (10 queries):
──────────────────────────────

Sequential: 260ms × 10 = 2,600ms
Concurrent: ~400ms (parallel processing!)

                Query 1 ──────────────────> Result 1
                Query 2 ──────────────────> Result 2
Time:  0ms      Query 3 ──────────────────> Result 3
   │            Query 4 ──────────────────> Result 4
   │            Query 5 ──────────────────> Result 5
   │            Query 6 ──────────────────> Result 6
   │            Query 7 ──────────────────> Result 7
   │            Query 8 ──────────────────> Result 8
   │            Query 9 ──────────────────> Result 9
   ▼            Query 10 ─────────────────> Result 10
 400ms         All complete!
```

## Integration Points

```
┌────────────────────────────────────────────────────────────────┐
│                    SYSTEM INTEGRATION MAP                       │
└────────────────────────────────────────────────────────────────┘

UI Layer (Next.js)
    │
    ├─ /src/app/api/copilotkit/route.ts
    │   └─ Proxies requests to agent backend
    │
Backend Agent (FastAPI)
    │
    ├─ agent/agent.py
    │   ├─ retail_coordinator (main agent)
    │   │   └─ sub_agents[]
    │   │       ├─ product_search_agent ← YOU ARE HERE
    │   │       ├─ review_text_analysis_agent
    │   │       ├─ inventory_agent
    │   │       └─ customer_support_agent
    │   │
    │   └─ product_search_agent/
    │       ├─ agent.py (ADK agent definition)
    │       ├─ tools.py (search functions)
    │       └─ __init__.py
    │
Image Pipeline (Python)
    │
    └─ image_embeddings_pipeline/
        ├─ config/config.py (shared config)
        ├─ src/
        │   ├─ search_engine.py ← USED BY TOOLS
        │   ├─ embedding_generator.py
        │   ├─ image_processor.py
        │   └─ qdrant_manager.py
        └─ main.py (indexing script)

External Services
    │
    ├─ NVIDIA NIM API
    │   └─ integrate.api.nvidia.com/v1/embeddings
    │
    └─ Qdrant Vector DB
        └─ localhost:6333
```

## Configuration Flow

```
┌────────────────────────────────────────────────────────────────┐
│                   CONFIGURATION HIERARCHY                       │
└────────────────────────────────────────────────────────────────┘

.env file (image_embeddings_pipeline/.env)
    │
    ├─ NVIDIA_API_KEY=nvapi-...
    ├─ NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
    ├─ QDRANT_URL=http://localhost:6333
    ├─ COLLECTION_NAME=image_embeddings
    └─ EMBEDDING_DIM=4096
    │
    ▼
config/config.py
    │
    ├─ Config.from_env()
    │   ├─ NvidiaConfig
    │   ├─ QdrantConfig
    │   └─ ProcessingConfig
    │
    ▼
Tools (tools.py)
    │
    ├─ _get_search_engine()
    │   └─ ImageSearchEngine(config)
    │       ├─ Uses NvidiaConfig for API calls
    │       ├─ Uses QdrantConfig for DB connection
    │       └─ Uses ProcessingConfig for optimization
    │
    ▼
Agent executes tools with validated configuration
```

## Error Handling Flow

```
┌────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING CHAIN                         │
└────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌───────────────────────┐
│ Input Validation      │  ← Empty query? Invalid URL?
│ ✗ Error: Return clear│    Return: {"error": "message"}
│   message to user     │
└───────────────────────┘
    │ ✓ Valid
    ▼
┌───────────────────────┐
│ Config Loading        │  ← Missing API key? Bad config?
│ ✗ Error: RuntimeError│    Return: {"error": "config issue"}
│   with setup steps    │
└───────────────────────┘
    │ ✓ Loaded
    ▼
┌───────────────────────┐
│ NVIDIA API Call       │  ← Network error? Rate limit?
│ ✗ Error: Retry logic │    Return: {"error": "API issue"}
│   then fallback       │
└───────────────────────┘
    │ ✓ Embedding generated
    ▼
┌───────────────────────┐
│ Qdrant Search         │  ← Connection error? Collection missing?
│ ✗ Error: Clear        │    Return: {"error": "DB issue"}
│   troubleshooting msg │
└───────────────────────┘
    │ ✓ Results found
    ▼
┌───────────────────────┐
│ Format Results        │  ← Data parsing error?
│ ✗ Error: Return safe │    Return: partial results or error
│   partial results     │
└───────────────────────┘
    │ ✓ Success
    ▼
Return formatted results to user
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCT SEARCH AGENT                            │
│                    Quick Reference Card                          │
└─────────────────────────────────────────────────────────────────┘

📍 Location: nvdia-ag-ui/agent/product_search_agent/

📂 Key Files:
   • agent.py         - Agent definition (Google ADK)
   • tools.py         - Search functions
   • README.md        - Full documentation
   • QUICKSTART.md    - 5-minute setup
   • test_agent.py    - Test suite

🔧 Setup Commands:
   docker run -d -p 6333:6333 qdrant/qdrant
   cd image_embeddings_pipeline
   python main.py 0 100

🎯 Core Functions:
   • search_products_by_text(query, limit, threshold)
   • search_products_by_image(url, limit, threshold)
   • search_with_filters(query, filters, limit)
   • get_collection_stats()
   • get_product_by_id(id)

📊 Similarity Scores:
   0.9-1.0: Extremely similar
   0.8-0.9: Very similar
   0.7-0.8: Similar (recommended threshold)
   0.6-0.7: Somewhat similar

⚡ Performance:
   Text search:  ~210ms
   Image search: ~510ms
   Vector search: ~10ms

🔗 Dependencies:
   • NVIDIA NIM API (embeddings)
   • Qdrant (vector DB)
   • Google ADK (agent framework)

📞 Test:
   python test_agent.py

🚀 Run:
   npm run dev (in nvdia-ag-ui/)
```
