# NVIDIA Retail AI - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (Browser)                           │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     Next.js 15 Application                              │ │
│  │                                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │ │
│  │  │              │  │              │  │              │  │            │ │ │
│  │  │  CopilotKit  │  │    React     │  │  Tailwind    │  │  Custom    │ │ │
│  │  │  Components  │  │    Hooks     │  │     CSS      │  │   Sidebar  │ │ │
│  │  │              │  │              │  │              │  │            │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │ │
│  │                                                                          │ │
│  │  CopilotSidebar          useCoAgent            Dashboard                │ │
│  │  Chat Interface          useCopilotAction      Results Grid             │ │
│  │                          useCopilotReadable    Tab Navigation           │ │
│  │                          useCopilotChatSuggestions                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/WebSocket
                                      │ AG-UI Protocol
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT BACKEND (FastAPI + Google ADK)                      │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     Google ADK Agent Runtime                            │ │
│  │                                                                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  LlmAgent: retail_ai_agent                                        │  │ │
│  │  │  Model: gemini-2.0-flash-exp                                      │  │ │
│  │  │                                                                    │  │ │
│  │  │  Callbacks:                                                        │  │ │
│  │  │  • on_before_agent     → Initialize state                         │  │ │
│  │  │  • before_model_modifier → Inject context                         │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  FunctionTools (4 Tools)                                          │  │ │
│  │  │                                                                    │  │ │
│  │  │  1. search_documents_tool                                         │  │ │
│  │  │     ├─ Query: retail compliance docs                              │  │ │
│  │  │     └─ Returns: Document results + updates state                  │  │ │
│  │  │                                                                    │  │ │
│  │  │  2. search_images_tool                                            │  │ │
│  │  │     ├─ Query: fashion product images                              │  │ │
│  │  │     └─ Returns: Image results + updates state                     │  │ │
│  │  │                                                                    │  │ │
│  │  │  3. analyze_inventory_tool                                        │  │ │
│  │  │     ├─ Category: product category                                 │  │ │
│  │  │     └─ Returns: Analysis + insights                               │  │ │
│  │  │                                                                    │  │ │
│  │  │  4. get_state_tool                                                │  │ │
│  │  │     └─ Returns: Current agent state                               │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  State Management (ToolContext)                                   │  │ │
│  │  │                                                                    │  │ │
│  │  │  • documents: List[SearchResult]                                  │  │ │
│  │  │  • images: List[SearchResult]                                     │  │ │
│  │  │  • inventory: List[InventoryItem]                                 │  │ │
│  │  │  • queries: List[str]                                             │  │ │
│  │  │  • current_analysis: Optional[Analysis]                           │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Python API Calls
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINES & SERVICES                             │
│                                                                              │
│  ┌────────────────┐         ┌────────────────┐         ┌────────────────┐  │
│  │   Document     │         │     Image      │         │   Inventory    │  │
│  │   Pipeline     │         │    Pipeline    │         │     Data       │  │
│  │                │         │                │         │                │  │
│  │  Docling PDF   │         │  Async Image   │         │   CSV Data     │  │
│  │  Extraction    │         │  Processing    │         │   Analytics    │  │
│  │                │         │                │         │                │  │
│  │  Text Chunking │         │  Resize/Encode │         │  Pandas DF     │  │
│  └────────────────┘         └────────────────┘         └────────────────┘  │
│          │                          │                          │            │
│          │                          │                          │            │
│          ↓                          ↓                          ↓            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │             NVIDIA AI Embeddings (API)                              │    │
│  │                                                                      │    │
│  │  Model: nvidia/llama-3.2-nemoretriever-300m-embed-v2               │    │
│  │  Dimensions: 2048                                                   │    │
│  │  Token Limit: 8192                                                  │    │
│  │  Input Types: query (search) / passage (documents)                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│          │                                                                   │
│          ↓                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │             Qdrant Vector Database                                  │    │
│  │                                                                      │    │
│  │  Collections:                                                       │    │
│  │  • document_embeddings  (retail compliance docs)                   │    │
│  │  • image_embeddings     (fashion products)                         │    │
│  │  • customer_support_docs                                           │    │
│  │                                                                      │    │
│  │  Distance: COSINE                                                   │    │
│  │  Port: 6333                                                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│          │                                                                   │
│          ↓                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │             NVIDIA Reranker (Optional)                              │    │
│  │                                                                      │    │
│  │  Model: nvidia/llama-3.2-nv-rerankqa-1b-v2                         │    │
│  │  Purpose: Refine top-k results for precision                       │    │
│  │  Usage: After vector search                                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

DATA FLOW EXAMPLE: Document Search

1. User types: "Search for safety compliance documents"
   └─> CopilotSidebar (React)

2. Message sent via AG-UI protocol
   └─> FastAPI /api/copilotkit endpoint

3. Google ADK Agent processes request
   ├─> Gemini 2.0 analyzes intent
   └─> Decides to call search_documents_tool

4. Tool execution
   ├─> Calls customer_support/src/retrieval.py
   ├─> Generates query embedding (NVIDIA API)
   ├─> Searches Qdrant vector DB
   ├─> Reranks results (NVIDIA Reranker)
   └─> Updates ToolContext state

5. Response streaming
   ├─> Agent formats response with results
   └─> AG-UI streams back to frontend

6. UI update
   ├─> useCoAgent receives state update
   ├─> searchResults state updated
   ├─> Dashboard re-renders
   └─> Results displayed in grid

═══════════════════════════════════════════════════════════════════════════════

KEY TECHNOLOGIES

Frontend:
• Next.js 15 (React Server Components)
• CopilotKit (AG-UI Protocol)
• TypeScript (Type Safety)
• Tailwind CSS (Styling)

Backend:
• Google ADK (Agent Framework)
• FastAPI (API Server)
• Pydantic (Data Validation)
• Gemini 2.0 (LLM)

AI & Data:
• NVIDIA nemoretriever (Embeddings)
• NVIDIA rerankqa (Reranking)
• Qdrant (Vector Database)
• Docling (PDF Extraction)

═══════════════════════════════════════════════════════════════════════════════

DEPLOYMENT ARCHITECTURE (Future)

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │     │  Cloud Run  │     │  Cloud Run  │
│  (Next.js)  │────▶│   (Agent)   │────▶│  (Qdrant)   │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ↓
                    ┌─────────────┐
                    │  NVIDIA AI  │
                    │   Cloud     │
                    └─────────────┘
```
