# Customer Support Agent - Architecture Diagram

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
│                 Next.js 15 + CopilotKit                         │
│                  http://localhost:3000                          │
│                                                                  │
│  Components:                                                     │
│  • ChatInterface.tsx - Main chat UI                            │
│  • Sidebar.tsx - Agent selector                                │
│  • CopilotKit Provider - Agent integration                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ WebSocket / HTTP
                         │ CopilotKit Protocol
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT BACKEND                                │
│              FastAPI + Google ADK + Gemini                      │
│                  http://localhost:8000                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           retail_coordinator (Main Agent)                │  │
│  │                 Gemini 2.5 Flash                         │  │
│  │                                                          │  │
│  │  Responsibilities:                                        │  │
│  │  • Analyze user requests                                 │  │
│  │  • Route to appropriate sub-agent                        │  │
│  │  • Coordinate multi-agent workflows                      │  │
│  │  • Synthesize responses                                  │  │
│  │                                                          │  │
│  │  Available Sub-Agents:                                   │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │ 🔍 product_search_agent                       │     │  │
│  │  │    - Fashion product search                    │     │  │
│  │  │    - Image/text queries                       │     │  │
│  │  │    - NVIDIA multimodal embeddings             │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │ 📊 review_text_analysis_agent                 │     │  │
│  │  │    - Customer review analysis                  │     │  │
│  │  │    - Sentiment scoring                         │     │  │
│  │  │    - Walmart reviews dataset                   │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │ 📦 inventory_agent                            │     │  │
│  │  │    - Stock availability                        │     │  │
│  │  │    - Warehouse + retail data                   │     │  │
│  │  │    - Delivery estimates                        │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │ 🛒 shopping_agent                             │     │  │
│  │  │    - Cart management                           │     │  │
│  │  │    - Checkout processing                       │     │  │
│  │  │    - Discount application                      │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │ 💬 customer_support_agent ⭐ NEW!            │     │  │
│  │  │    - Policy Q&A                               │     │  │
│  │  │    - RAG retrieval                            │     │  │
│  │  │    - Document citations                        │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CUSTOMER SUPPORT TOOLS MODULE                       │
│                   (tools.py)                                     │
│                                                                  │
│  class CustomerSupportTools:                                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  search_policy_documents(query, top_k)               │      │
│  │  ─────────────────────────────────────               │      │
│  │  Inputs:                                              │      │
│  │  • query: str - Customer question                    │      │
│  │  • top_k: int - Number of results (default: 5)      │      │
│  │                                                       │      │
│  │  Process:                                             │      │
│  │  1. Generate query embedding                         │      │
│  │  2. Vector search in Qdrant                          │      │
│  │  3. Neural reranking                                 │      │
│  │  4. Format results with metadata                     │      │
│  │                                                       │      │
│  │  Output:                                              │      │
│  │  • Ranked document chunks                            │      │
│  │  • Similarity scores                                 │      │
│  │  • Source citations                                  │      │
│  │  • Confidence metrics                                │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  get_collection_info()                                │      │
│  │  ─────────────────────                                │      │
│  │  Returns:                                             │      │
│  │  • Collection name                                    │      │
│  │  • Total document chunks                              │      │
│  │  • Database status                                    │      │
│  │  • Vector dimensions                                  │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────┬────────────────────┬───────────────────────────────┘
             │                    │
             ▼                    ▼
┌────────────────────────┐  ┌──────────────────────────────┐
│  RetrievalPipeline     │  │     QdrantManager            │
│  (retrieval.py)        │  │  (qdrant_manager.py)         │
│                        │  │                              │
│  Responsibilities:     │  │  Responsibilities:           │
│  • Query embedding     │  │  • Collection management     │
│  • Vector search       │  │  • Vector search             │
│  • Reranking           │  │  • Metadata filtering        │
│  • Result formatting   │  │  • Point insertion           │
└────────┬───────────────┘  └────────┬─────────────────────┘
         │                           │
         ▼                           ▼
┌────────────────────────┐  ┌──────────────────────────────┐
│    NVIDIA API          │  │    Qdrant Vector DB          │
│                        │  │                              │
│  Embedding Model:      │  │  Collection:                 │
│  llama-3.2-nemoretri-  │  │  customer_support_docs       │
│  ever-300m-embed-v2    │  │                              │
│                        │  │  Configuration:              │
│  • 2048 dimensions     │  │  • Distance: Cosine          │
│  • 8192 token context  │  │  • Vector size: 2048         │
│  • Input types:        │  │  • Storage: Persistent       │
│    - query             │  │  • Port: 6333                │
│    - passage           │  │                              │
│                        │  │  Point Structure:            │
│  Reranker Model:       │  │  • id: unique int            │
│  llama-3.2-nv-rerank-  │  │  • vector: [2048 floats]     │
│  qa-1b-v2              │  │  • payload:                  │
│                        │  │    - text                    │
│  • Contextual scoring  │  │    - chunk_id                │
│  • Top-k refinement    │  │    - source_filename         │
│                        │  │    - metadata                │
│                        │  │    - timestamps              │
└────────────────────────┘  └──────────────────────────────┘
```

## Data Flow: Query to Response

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User Query                                          │
└─────────────────────────────────────────────────────────────┘
   
   User: "What is your return policy for electronics?"
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Frontend Processing                                 │
└─────────────────────────────────────────────────────────────┘
   
   CopilotKit → Send to agent backend
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: retail_coordinator Analysis                         │
└─────────────────────────────────────────────────────────────┘
   
   Coordinator: "This is a policy question"
   Decision: Route to customer_support_agent
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: customer_support_agent Tool Call                    │
└─────────────────────────────────────────────────────────────┘
   
   Agent calls: search_policy_documents(
     query="What is your return policy for electronics?",
     top_k=5
   )
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: CustomerSupportTools Processing                     │
└─────────────────────────────────────────────────────────────┘
   
   5a. Generate Query Embedding
   ────────────────────────────
   Input: "What is your return policy for electronics?"
   
   NVIDIA API Request:
   {
     "input": "What is your return policy...",
     "model": "llama-3.2-nemoretriever-300m-embed-v2",
     "input_type": "query",  ← Important!
     "truncate": "NONE"
   }
   
   Output: [0.234, -0.567, 0.891, ... ] (2048 floats)
   
   │
   ▼
   
   5b. Vector Search in Qdrant
   ────────────────────────────
   Query Vector: [2048 floats]
   Collection: customer_support_docs
   Limit: 20 candidates
   Distance: Cosine similarity
   
   Results: 20 document chunks sorted by similarity
   
   Example result:
   {
     "id": 42,
     "score": 0.87,  ← Vector similarity
     "payload": {
       "text": "Electronics return policy: 30 days...",
       "source_filename": "Returns_Policy_2024.pdf",
       "chunk_index": 5,
       ...
     }
   }
   
   │
   ▼
   
   5c. Neural Reranking
   ────────────────────
   NVIDIA Reranker API Request:
   {
     "query": "What is your return policy for electronics?",
     "passages": [
       "Electronics return policy: 30 days...",
       "General return policy...",
       ...
     ],
     "model": "llama-3.2-nv-rerankqa-1b-v2"
   }
   
   Output: Rerank scores for each passage
   [0.92, 0.85, 0.78, 0.71, 0.65, ...]
   
   Top 5 after reranking:
   1. Chunk 42 - Rerank: 0.92, Vector: 0.87
   2. Chunk 15 - Rerank: 0.85, Vector: 0.81
   3. Chunk 28 - Rerank: 0.78, Vector: 0.84
   4. Chunk 7  - Rerank: 0.71, Vector: 0.79
   5. Chunk 33 - Rerank: 0.65, Vector: 0.76
   
   │
   ▼
   
   5d. Format Results
   ──────────────────
   Return to agent:
   {
     "success": true,
     "results_count": 5,
     "results": [
       {
         "rank": 1,
         "text": "Electronics can be returned...",
         "source_filename": "Returns_Policy_2024.pdf",
         "chunk_index": 5,
         "similarity_score": 0.87,
         "rerank_score": 0.92,
         "metadata": {...}
       },
       ...
     ]
   }
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Agent Response Generation                           │
└─────────────────────────────────────────────────────────────┘
   
   customer_support_agent (Gemini 2.0):
   
   Input:
   • Original query
   • Top 5 ranked document chunks
   • Metadata and scores
   
   Processing:
   • Analyze retrieved content
   • Extract relevant information
   • Generate natural language response
   • Include citations and confidence
   
   │
   ▼
   
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Response Delivered to User                          │
└─────────────────────────────────────────────────────────────┘
   
   **Return Policy for Electronics**:
   
   According to our Returns and Exchanges Policy (chunk 5):
   "Electronic items may be returned within 30 days of 
   purchase with original packaging, accessories, and proof 
   of purchase. Items must be in new, unused condition."
   
   **Additional Details**:
   - Restocking fee: 15% for opened electronics
   - Warranty items: Different process applies
   - Receipt required for all returns
   
   **Confidence**: 0.92/1.0 (Rerank Score)
   **Source**: Returns_Policy_2024.pdf, Section 3.2
```

## Document Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Document Ingestion (One-time Setup)                         │
└─────────────────────────────────────────────────────────────┘

Customer places PDFs in:
customer_support/data/
├── Returns_Policy_2024.pdf
├── Warranty_Guidelines.pdf
├── Shipping_Policy.pdf
└── Customer_Rights.pdf

│
▼

┌─────────────────────────────────────────────────────────────┐
│ python main.py process ./data                               │
└─────────────────────────────────────────────────────────────┘

1. Document Loading (load_data.py)
   ──────────────────────────────
   • Scan data/ directory
   • Detect PDF files
   • Extract text with Docling
   • Preserve structure and metadata
   
   Output: Raw text + document metadata

│
▼

2. Chunking (chunking.py)
   ──────────────────────
   • Split text into chunks
   • Size: 512 tokens (configurable)
   • Overlap: 50 tokens (prevents info loss)
   • Assign chunk IDs and indices
   
   Example chunk:
   {
     "text": "Electronics can be returned...",
     "chunk_id": "returns_policy_chunk_005",
     "chunk_index": 5,
     "source_filename": "Returns_Policy_2024.pdf",
     "source_filepath": "/data/Returns_Policy_2024.pdf",
     "char_count": 487,
     "metadata": {...}
   }
   
   Output: 187 chunks (for 5 documents)

│
▼

3. Embedding Generation (embedding.py)
   ───────────────────────────────────
   • Batch process chunks (10 per batch)
   • Call NVIDIA API for embeddings
   • input_type: "passage" ← For documents
   • Model: llama-3.2-nemoretriever-300m-embed-v2
   
   For each chunk:
   {
     ...previous_data,
     "embedding": [2048 floats],
     "embedding_dim": 2048
   }
   
   Output: 187 chunks with embeddings

│
▼

4. Qdrant Insertion (qdrant_manager.py)
   ────────────────────────────────────
   • Create collection if not exists
   • Insert points in batches (100)
   • Store vectors + metadata
   • Index for fast search
   
   Collection: customer_support_docs
   Points: 187
   Status: ✅ Ready for search

│
▼

✅ Documents indexed and searchable!
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────┐
│                  Component Matrix                         │
└──────────────────────────────────────────────────────────┘

Component               │ Depends On           │ Provides
────────────────────────┼─────────────────────┼──────────────
CustomerSupportTools    │ • RetrievalPipeline  │ • search_policy
                        │ • QdrantManager      │ • get_info
                        │ • Config             │
────────────────────────┼─────────────────────┼──────────────
RetrievalPipeline       │ • EmbeddingGenerator │ • search()
                        │ • QdrantManager      │ • rerank()
                        │ • NVIDIA API         │
────────────────────────┼─────────────────────┼──────────────
EmbeddingGenerator      │ • NVIDIA API         │ • generate_
                        │ • OpenAI client      │   embedding()
────────────────────────┼─────────────────────┼──────────────
QdrantManager           │ • Qdrant client      │ • search()
                        │ • Config             │ • insert()
                        │                      │ • get_info()
────────────────────────┼─────────────────────┼──────────────
customer_support_agent  │ • CustomerSupport-   │ • Agent
                        │   Tools              │   instance
                        │ • Google ADK         │
                        │ • Gemini API         │
────────────────────────┼─────────────────────┼──────────────
retail_coordinator      │ • All sub-agents     │ • Main
                        │ • Google ADK         │   coordinator
                        │ • Gemini API         │
```

## File Structure

```
nvdia-ag-ui/
├── agent/
│   ├── agent.py ← Main coordinator
│   │
│   └── customer_support_agent/ ⭐ NEW!
│       ├── __init__.py
│       ├── agent.py ← Agent definition
│       ├── tools.py ← Tool implementations
│       ├── test_agent.py ← Test suite
│       ├── README.md ← Full documentation
│       ├── QUICKSTART.md ← Setup guide
│       ├── IMPLEMENTATION_SUMMARY.md ← This summary
│       └── ARCHITECTURE.md ← Architecture diagrams

customer_support/
├── config/
│   ├── __init__.py
│   └── config.py ← Configuration classes
├── src/
│   ├── __init__.py
│   ├── retrieval.py ← RetrievalPipeline
│   ├── qdrant_manager.py ← QdrantManager
│   ├── embedding.py ← EmbeddingGenerator
│   ├── chunking.py ← Text chunking
│   └── load_data.py ← Document loading
├── data/ ← PDF policy documents
├── main.py ← Processing script
└── requirements.txt ← Python dependencies
```

---

**Legend**:
- 📄 Documents
- 🔍 Search operations
- 💬 Chat/Communication
- 📊 Analytics
- ⭐ New/Featured
- ✅ Ready/Complete
- 🔧 Configuration
