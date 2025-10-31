# Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     NVIDIA AI Teams System                      │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│   Document        │  │   Image           │  │   AI Agent UI    │
│   Pipeline        │  │   Pipeline        │  │   (CopilotKit)   │
│  (Customer_       │  │                   │  │                   │
│   support/Code)   │  │                   │  │                   │
│  • PDF Extract    │  │  • Image Download │  │  • Next.js 15    │
│  • Chunking       │  │  • Resize/Encode  │  │  • React UI      │
│  • Embeddings     │  │  • Embeddings     │  │  • Python Agent  │
│  • Reranking      │  │  • Search         │  │                  │
└────────┬──────────┘  └────────┬──────────┘  └────────┬─────────┘
         │                      │                       │
         └──────────────┬───────┴───────────────────────┘
                        ↓
         ┌──────────────────────────────┐
         │    Qdrant Vector Database    │
         │                              │
         │  Collections:                │
         │  • customer_support_docs     │
         │  • image_embeddings          │
         │  • document_embeddings       │
         └──────────────────────────────┘
                        ↓
         ┌──────────────────────────────┐
         │       NVIDIA AI APIs         │
         │                              │
         │  • NeMo Retriever Embeddings │
         │  • Reranking Model           │
         │  • OCR (optional)            │
         └──────────────────────────────┘
```

## Document Processing Pipeline (Detailed)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Document Processing Flow                       │
└──────────────────────────────────────────────────────────────────┘

  PDF Files                     Text Extraction
  ┌─────────┐                   ┌───────────────┐
  │ Doc 1   │──────────────────→│ DoclingExtractor│
  │ Doc 2   │   Docling Library │ • Structured   │
  │ Doc 3   │   • Tables        │ • Page numbers │
  └─────────┘   • Metadata      │ • Metadata     │
                                └───────┬─────────┘
                                        ↓
                                  Text Documents
                                        ↓
                                ┌──────────────┐
                                │ TextChunker  │
                                │ • Size: 512  │
                                │ • Overlap: 50│
                                └──────┬───────┘
                                       ↓
                                  Chunks (with context)
                                       ↓
                          ┌────────────────────────┐
                          │ EmbeddingGenerator    │
                          │ NVIDIA API            │
                          │ • input_type=passage  │
                          │ • 300-dim vectors     │
                          └──────────┬────────────┘
                                     ↓
                              Embeddings (vectors)
                                     ↓
                          ┌─────────────────────┐
                          │  QdrantVectorDB     │
                          │  • Store vectors    │
                          │  • Store metadata   │
                          │  • Store content    │
                          └─────────────────────┘
```

## Retrieval Pipeline (Two-Stage)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Two-Stage Retrieval Flow                       │
└──────────────────────────────────────────────────────────────────┘

  User Query: "retail compliance requirements"
        ↓
  ┌─────────────────────┐
  │ EmbeddingGenerator  │  Stage 1: Query Understanding
  │ • input_type=query  │  Convert text to vector
  │ • 300-dim vector    │
  └──────────┬──────────┘
             ↓
       Query Vector
             ↓
  ┌─────────────────────┐
  │  Vector Search      │  Stage 2: Fast Retrieval
  │  (Qdrant)           │  Find similar vectors
  │  • Cosine similarity│  Get top 50 candidates
  │  • Top 50 results   │
  └──────────┬──────────┘
             ↓
       50 Candidates
             ↓
  ┌─────────────────────┐
  │  Reranker           │  Stage 3: Precision Refinement
  │  (NVIDIA)           │  Deep cross-attention
  │  • Cross-attention  │  Reorder by relevance
  │  • Top 10 results   │  Return best matches
  └──────────┬──────────┘
             ↓
       10 Best Results
             ↓
  ┌─────────────────────┐
  │  User / RAG System  │  Ready for:
  │  • Content          │  • Display to user
  │  • Scores           │  • Feed to LLM
  │  • Metadata         │  • Generate answer
  │  • Citations        │
  └─────────────────────┘
```

## SOLID Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      SOLID Principles in Action                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Single Responsibility Principle (SRP)                           │
│                                                                 │
│  DoclingExtractor    →  Only extracts PDFs                     │
│  TextChunker         →  Only chunks text                       │
│  EmbeddingGenerator  →  Only generates embeddings              │
│  VectorDB            →  Only manages database                  │
│  Reranker            →  Only reranks results                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Interface Segregation Principle (ISP)                          │
│                                                                 │
│  IDocumentExtractor  ──→  extract(file_path)                  │
│  ITextChunker        ──→  chunk(document)                     │
│  IEmbeddingGenerator ──→  generate_embedding(text)            │
│  IVectorDatabase     ──→  search(vector, top_k)               │
│  IReranker           ──→  rerank(query, results)              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Dependency Injection Pattern                                    │
│                                                                 │
│  class RetrievalPipeline:                                      │
│      def __init__(                                             │
│          self,                                                 │
│          embedder: IEmbeddingGenerator,    # Interface        │
│          vector_db: IVectorDatabase,       # Interface        │
│          reranker: IReranker,              # Interface        │
│          config: RetrievalConfig           # Dataclass        │
│      ):                                                        │
│          self.embedder = embedder          # Injected         │
│          self.vector_db = vector_db        # Injected         │
│          self.reranker = reranker          # Injected         │
│                                                                │
│  Benefits:                                                     │
│  ✓ Easy to test (inject mocks)                                │
│  ✓ Easy to swap implementations                               │
│  ✓ No hidden dependencies                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Open/Closed Principle (OCP)                                     │
│                                                                 │
│  Want to add Word document support?                            │
│                                                                 │
│  class WordExtractor(IDocumentExtractor):  # New class        │
│      async def extract(self, file_path):   # Implement        │
│          # Your Word extraction logic                          │
│          pass                                                  │
│                                                                 │
│  extractor = WordExtractor()               # Use it           │
│  processor = DocumentProcessor(extractor, ...)                 │
│                                                                 │
│  No existing code changed! ✓                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

```
┌──────────────────────────────────────────────────────────────────┐
│               Example: Processing a PDF Document                  │
└──────────────────────────────────────────────────────────────────┘

Step 1: PDF Input
├─ File: RegulatedProductsHandbook.pdf
├─ Size: 45 pages
└─ Content: Retail compliance guidelines

Step 2: Extraction (Docling)
├─ Extract text from 45 pages
├─ Detect 12 tables
├─ Preserve formatting
└─ Output: 45 Document objects

Step 3: Chunking
├─ Split into 512-word chunks
├─ 50-word overlap
├─ Result: 342 chunks
└─ Metadata: page numbers, positions

Step 4: Embedding Generation
├─ Generate embedding for each chunk
├─ Model: llama-3.2-nemoretriever-300m-embed-v2
├─ Input type: "passage"
├─ Result: 342 × 300-dim vectors
└─ Time: ~45 seconds

Step 5: Storage (Qdrant)
├─ Upsert 342 points
├─ Vector + payload (content, metadata)
├─ Collection: customer_support_docs
└─ Ready for search!

Step 6: Query "retail compliance requirements"
├─ Generate query embedding
├─ Vector search: top 50 results
├─ Rerank: top 10 results
├─ Response time: ~2.3 seconds
└─ Return: Relevant chunks with citations

┌──────────────────────────────────────────────────────────────────┐
│                      Query Results                                │
└──────────────────────────────────────────────────────────────────┘

Result 1: Score 0.8923
├─ Source: RegulatedProductsHandbook.pdf
├─ Page: 12
└─ Content: "Retail compliance requirements mandate that..."

Result 2: Score 0.8756
├─ Source: Retail Program Standards Policy Statement.pdf
├─ Page: 5
└─ Content: "All retail establishments must comply with..."

Result 3: Score 0.8634
├─ Source: tclc-fs-fedreg-retail-environ-2012.pdf
├─ Page: 8
└─ Content: "Environmental compliance standards require..."
```

## Component Interaction

```
┌───────────────────────────────────────────��──────────────────────┐
│              Component Interaction Diagram                        │
└──────────────────────────────────────────────────────────────────┘

Main CLI
   │
   ├─→ Config.from_env()
   │      │
   │      └─→ Validate()
   │
   ├─→ Create Components (DI)
   │      │
   │      ├─→ DoclingExtractor()
   │      ├─→ OverlapTextChunker(config)
   │      ├─→ NvidiaEmbeddingGenerator(config)
   │      ├─→ QdrantVectorDB(config)
   │      └─→ NvidiaReranker(config)
   │
   ├─→ DocumentProcessor(extractor, chunker, embedder, vector_db)
   │      │
   │      └─→ process_directory()
   │             │
   │             ├─→ extractor.extract()    [PDF → Text]
   │             ├─→ chunker.chunk()        [Text → Chunks]
   │             ├─→ embedder.generate()    [Chunks → Vectors]
   │             └─→ vector_db.upsert()     [Store in Qdrant]
   │
   └─→ RetrievalPipeline(embedder, vector_db, reranker, config)
          │
          └─→ retrieve()
                 │
                 ├─→ embedder.generate()    [Query → Vector]
                 ├─→ vector_db.search()     [Vector → Results]
                 └─→ reranker.rerank()      [Results → Top K]
```

## Technology Stack

```
┌──────────────────────────────────────────────────────────────────┐
│                      Technology Stack                             │
└──────────────────────────────────────────────────────────────────┘

Backend Processing
├─ Python 3.8+
├─ asyncio (async/await)
├─ aiohttp (HTTP client)
└─ typing (type hints)

PDF Processing
├─ Docling
│  ├─ Structured extraction
│  ├─ Table detection
│  └─ Metadata preservation

AI / ML
├─ OpenAI Python SDK
├─ NVIDIA AI Endpoints
│  ├─ llama-3.2-nemoretriever-300m-embed-v2 (embeddings)
│  ├─ llama-3.2-nv-rerankqa-1b-v2 (reranking)
│  └─ nemoretriever-ocr-v1 (OCR - optional)

Vector Database
├─ Qdrant
│  ├─ HNSW indexing
│  ├─ Cosine similarity
│  └─ Metadata filtering

Configuration
├─ python-dotenv
├─ dataclasses
└─ typing

Frontend (AI Agent)
├─ Next.js 15
├─ React 19
├─ CopilotKit
└─ TypeScript

Infrastructure
├─ Docker (Qdrant)
└─ Git
```
