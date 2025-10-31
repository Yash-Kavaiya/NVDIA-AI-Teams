# NVIDIA AI Teams - Development Guide

## Architecture Overview

This is a **multi-modal AI system** combining document processing, image embeddings, and conversational AI with three main components:

1. **Image Embeddings Pipeline** (`image_embeddings_pipeline/`) - Async Python pipeline for processing images and generating embeddings using NVIDIA's nv-embed-v1 model
2. **AI Agent UI** (`nvdia-ag-ui/`) - Next.js 15 + CopilotKit frontend with Python agent backend
3. **Customer Support Document Pipeline** (`Customer_support/Code/document_pipeline/`) - Document processing and RAG system for retail compliance PDFs

### Data Flow
```
PDFs (Data/) → Docling extraction → Text chunks → NVIDIA embeddings → Qdrant vector DB
Images (CSV) → Download → Resize/encode → NVIDIA embeddings → Qdrant vector DB
User queries → Text embeddings → Qdrant search → Reranker → Results
```

## Critical Conventions

### Python Code Structure (SOLID Principles Required)
- **Single Responsibility**: Each class has ONE job (see `EmbeddingGenerator`, `QdrantManager`, `ImageProcessor`)
- **Dependency Injection**: Pass config objects to constructors, never use globals
- **Interface Segregation**: Create abstract base classes for generators, managers, and processors
- **Async-First**: All I/O operations MUST use `asyncio` and `aiohttp` for concurrency

Example pattern from `src/pipeline.py`:
```python
class ImageEmbeddingPipeline:
    def __init__(self, config: Config):
        self.qdrant_manager = QdrantManager(config.qdrant)  # DI
        self.embedding_generator = EmbeddingGenerator(config.nvidia, config.processing)
```

### Configuration Management
- Environment variables via `.env` (never commit API keys)
- Dataclass-based config in `config/config.py` with validation
- Required vars: `NVIDIA_API_KEY`, `NVIDIA_EMBEDDING_URL`, `QDRANT_URL`
- NVIDIA API key format: `nvapi-XXXXX` (integrate.api.nvidia.com)

### NVIDIA API Integration
**Embedding Model**: `nvidia/llama-3.2-nemoretriever-300m-embed-v2` (2048-dim vectors, 8192 token limit, 300M params)
```python
# Text/Query embeddings
extra_body={"input_type": "query", "truncate": "NONE"}
# Document/Passage embeddings  
extra_body={"input_type": "passage", "truncate": "NONE"}
```

**Reranker Model**: `nvidia/llama-3.2-nv-rerankqa-1b-v2` (use after retrieval for top-k refinement)

**OCR**: `nvidia/nemoretriever-ocr-v1` for PDF images/scanned docs (< 180KB base64 limit)

### Qdrant Vector Database
- Collection per domain: `image_embeddings`, `document_embeddings`, `customer_support_docs`
- Always use `Distance.COSINE` for similarity
- Point structure:
```python
PointStruct(id=unique_int, vector=embedding, payload={
    "source": "filename/url",
    "content": "original_text",  # for docs
    "metadata": {...},
    "processed_at": iso_timestamp
})
```

### Document Processing with Docling
- Install: `pip install docling`
- Extract PDFs from `Customer_support/Data/` → structured text + tables
- Chunk strategy: 512 tokens with 50 token overlap
- Store original page numbers in payload for citation

## Key Workflows

### Setup & Run
```bash
# Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# Document pipeline
cd Customer_support/Code/document_pipeline
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py process ../Data

# Image pipeline
cd image_embeddings_pipeline
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py [start_row] [max_images] [csv_path]

# AI UI (Next.js + Agent)
cd nvdia-ag-ui
npm install  # auto-installs Python agent deps
npm run dev  # runs UI + agent concurrently
```

### Testing
- Test files in `image_embeddings_pipeline/tests/`
- Run: `pytest tests/ -v`
- Mock NVIDIA API calls for unit tests

### Logging
- All modules use `logging` with file + console handlers
- Logs → `logs/pipeline.log`
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## AI Agent (CopilotKit)

Backend: `nvdia-ag-ui/agent/agent.py` - Python FastAPI server with CopilotKit SDK
Frontend: `src/app/api/copilotkit/route.ts` - Next.js API route proxy

Agent capabilities defined in Python using `@copilotkit_customize` decorators. State shared via React context.

## Retrieval & Reranking Pattern

1. **Generate query embedding** (input_type="query")
2. **Vector search** in Qdrant (top 20-50 results)
3. **Rerank** top candidates with `llama-3.2-nv-rerankqa-1b-v2`
4. **Return** top 5-10 after reranking

Implement as:
```python
class RetrievalPipeline:  # Interface Segregation
    def __init__(self, embedder: IEmbedder, db: IVectorDB, reranker: IReranker):
        ...
    async def search(self, query: str, top_k: int) -> List[Result]:
        ...
```

## Common Pitfalls

- **Don't** call NVIDIA API without retry logic (use exponential backoff)
- **Don't** process images synchronously (use `asyncio.Semaphore` for concurrency control)
- **Don't** store embeddings in memory for large datasets (stream to Qdrant in batches)
- **Always** validate Qdrant collection exists before operations
- **Always** encode images as base64 data URIs for NVIDIA API

## File Locations

- PDF documents: `Customer_support/Data/*.pdf`
- Document pipeline: `Customer_support/Code/document_pipeline/*.py`
- Image CSV: `image_embeddings_pipeline/data/images.csv`
- Config: `image_embeddings_pipeline/config/config.py`
- Core logic: `image_embeddings_pipeline/src/*.py`
- Agent backend: `nvdia-ag-ui/agent/agent.py`
