# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-modal AI system for retail operations combining:
- **Document processing pipeline** - RAG system for retail compliance PDFs using NVIDIA embeddings
- **Image embeddings pipeline** - Async visual search for fashion products
- **AI Agent UI** - Next.js 15 + Python ADK agents with specialized retail capabilities

## Development Commands

### AI Agent UI (Primary Development Interface)

```bash
cd nvdia-ag-ui
npm install              # Also runs postinstall to setup Python agent
npm run dev              # Runs UI (localhost:3000) + Agent backend (port 8000) concurrently
npm run dev:ui           # UI only
npm run dev:agent        # Agent backend only (requires .venv in agent/ directory)
npm run build            # Production build
npm run lint             # ESLint
npm run type-check       # TypeScript validation
```

### Image Embeddings Pipeline

```bash
cd image_embeddings_pipeline
python -m venv venv && source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py [start_row] [max_images] [csv_path]  # Index images to Qdrant
pytest tests/ -v         # Run tests
```

### Document Processing Pipeline

```bash
cd customer_support
pip install -r requirements.txt
python main.py process ../Data              # Index PDFs
python main.py search "query text"          # Search indexed docs
python main.py interactive                  # Interactive search mode
```

### Qdrant Vector Database

```bash
# Required for all pipelines
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
# Access dashboard: http://localhost:6333/dashboard
```

## Architecture

### Multi-Agent System (nvdia-ag-ui/agent/)

The system uses a **coordinator pattern** with specialized sub-agents:

**Main Coordinator**: `agent/agent.py` (retail_coordinator)
- Routes requests to appropriate specialized agents
- Orchestrates multi-agent workflows
- Manages conversation state via `ProverbsState` (legacy naming, used for general state)
- Runs on port 8000 (FastAPI + Google ADK + ag-ui-adk middleware)

**Active Sub-Agents**:
1. **product_search_agent/** - Visual search using NVIDIA nv-embed-v1 (4096-dim) + Qdrant
2. **review_text_analysis_agent/** - Customer review sentiment analysis with pandas
3. **inventory_agent/** - Sales analytics from `inventory_data/Warehouse_and_Retail_Sales.csv`

**Disabled Sub-Agents** (commented out in agent.py):
- `shopping_agent` - Not implemented
- `customer_support_agent` - Requires external `customer_support` module path setup

**Critical Import Pattern**: Use absolute imports, NOT relative imports in agent files:
```python
# CORRECT
from product_search_agent.agent import root_agent
# WRONG (will fail when run as script)
from .product_search_agent.agent import root_agent
```

### Frontend (Next.js 15 + CopilotKit)

- `src/app/page.tsx` - Main chat interface using @ag-ui/client
- CopilotKit connects to agent backend via `/api/copilotkit` proxy
- Uses Turbopack for dev server
- Tailwind CSS 4 for styling

### Image Search Pipeline Integration

Located in `image_embeddings_pipeline/src/`:
- `search_engine.py` - ImageSearchEngine class (used by product_search_agent)
- `image_processor.py` - Image download + base64 encoding (requires PIL)
- `embedding_generator.py` - NVIDIA API integration
- `qdrant_manager.py` - Vector DB operations

**Important**: product_search_agent imports these modules, so they must be importable. Dependencies include: `qdrant-client`, `pillow`, `pandas`, `aiohttp`

## Critical Configuration

### Environment Variables

**Agent Backend** (nvdia-ag-ui/agent/.env):
```bash
GOOGLE_API_KEY=your-google-ai-key  # Required for ADK agents
PORT=8000                           # Optional, defaults to 8000
```

**Image Pipeline** (image_embeddings_pipeline/.env):
```bash
NVIDIA_API_KEY=nvapi-XXXXX                                  # NVIDIA NIM API
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=image_embeddings
EMBEDDING_DIM=4096                                          # nv-embed-v1 dimensions
```

**Document Pipeline** (customer_support/.env):
```bash
NVIDIA_API_KEY=nvapi-XXXXX
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
NVIDIA_RERANKER_URL=https://integrate.api.nvidia.com/v1/ranking
QDRANT_URL=http://localhost:6333
```

### Python Dependencies

**Agent dependencies** are in `nvdia-ag-ui/agent/requirements.txt`:
```
fastapi, uvicorn[standard], google-adk, google-genai, ag-ui-adk, pandas>=2.0.0
```

**Additional runtime deps** (not in requirements.txt but needed by agents):
```
qdrant-client, pillow, aiohttp
```

Install all: `cd nvdia-ag-ui/agent && pip install -r requirements.txt qdrant-client pillow aiohttp`

## Data Locations

- Fashion images CSV: `image_embeddings_pipeline/data/images.csv`
- Inventory data: `inventory_data/Warehouse_and_Retail_Sales.csv`
- PDF documents: `customer_support/Data/*.pdf`
- Qdrant storage: Docker volume `qdrant_storage`

## NVIDIA Models Used

**Embeddings**:
- `nvidia/llama-3.2-nemoretriever-300m-embed-v2` (2048-dim, 8192 token limit) - Documents
- `nvidia/nv-embed-v1` (4096-dim) - Images and multimodal

**Reranker**:
- `nvidia/llama-3.2-nv-rerankqa-1b-v2` - Refine top-k retrieval results

**OCR** (optional):
- `nvidia/nemoretriever-ocr-v1` - Scanned PDFs (<180KB base64 images)

API calls require `input_type` parameter:
- `"query"` for search queries
- `"passage"` for indexed documents

## Key Architecture Patterns

### SOLID Principles (Document Pipeline)
All new Python code should follow these patterns from `customer_support/Code/document_pipeline/`:
- **Single Responsibility**: Separate classes for embedding, storage, retrieval
- **Dependency Injection**: Pass config objects to constructors
- **Interface Segregation**: Use abstract base classes (e.g., `IEmbedder`, `IVectorDB`)

### Async-First (Image Pipeline)
Use `asyncio` and `aiohttp` for all I/O:
```python
async def process_images(self, images: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [self._download_image(session, url) for url in images]
        return await asyncio.gather(*tasks)
```

### Google ADK Agent Pattern
```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

root_agent = LlmAgent(
    name="agent_name",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[FunctionTool(func=tool_function)],
    sub_agents=[child_agent1, child_agent2]  # Optional
)
```

### Qdrant Point Structure
```python
PointStruct(
    id=unique_int,
    vector=embedding_list,  # List[float] matching EMBEDDING_DIM
    payload={
        "source": "filename or URL",
        "content": "original text",
        "metadata": {...},
        "processed_at": "ISO timestamp"
    }
)
```

## Common Development Tasks

### Adding a New Agent

1. Create directory: `nvdia-ag-ui/agent/new_agent/`
2. Create files:
   - `__init__.py` - Export root_agent
   - `agent.py` - Define LlmAgent with tools
   - `tools.py` - Implement tool functions
   - `README.md` - Document capabilities
3. Import in `nvdia-ag-ui/agent/agent.py`:
   ```python
   from new_agent.agent import root_agent as new_agent
   ```
4. Add to coordinator's sub_agents list

### Troubleshooting Agent Startup

**Issue**: ModuleNotFoundError when running `npm run dev`

**Common causes**:
1. Missing Python dependency → Install in agent/.venv
2. Relative imports in agent files → Change to absolute imports
3. Missing external module (e.g., customer_support) → Comment out agent import
4. Wrong Python path → Verify `.venv/Scripts/python.exe` exists (Windows) or `.venv/bin/python` (Unix)

**Fix pattern**:
```bash
cd nvdia-ag-ui/agent
.venv/Scripts/pip install <missing-package>
# Then restart: npm run dev
```

### Vector Search Best Practices

**Two-stage retrieval** (document pipeline):
1. Qdrant search (top 20-50 results, fast)
2. NVIDIA reranker (top 5-10 refined, accurate)

**Score thresholds**:
- `0.9-1.0` - Near-exact matches
- `0.7-0.8` - Relevant results (recommended)
- `<0.6` - Too broad

**Query optimization**: More specific = better results
- Good: "red dress"
- Better: "red floral summer maxi dress"

## Testing

**Image Pipeline**:
```bash
cd image_embeddings_pipeline
pytest tests/ -v
# Mock NVIDIA API calls in tests
```

**Inventory Agent**:
```bash
cd nvdia-ag-ui/agent
python test_inventory_agent.py  # Comprehensive tool tests
```

**ADK Web Interface** (for any agent):
```bash
cd nvdia-ag-ui
adk web agent/inventory_agent    # Interactive web UI
adk run agent/inventory_agent    # CLI interface
```

## Logging

All modules use Python `logging`:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
```

Logs written to `logs/pipeline.log` with format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Performance Considerations

- **NVIDIA API**: Use exponential backoff retry logic (rate limits apply)
- **Image processing**: Limit concurrent downloads with `asyncio.Semaphore`
- **Large datasets**: Stream to Qdrant in batches, don't hold all embeddings in memory
- **Base64 encoding**: NVIDIA OCR has <180KB limit per image
- **Qdrant**: Always check collection exists before operations

## Known Issues

1. **shopping_agent not implemented** - Import commented out in agent.py
2. **customer_support_agent requires sys.path setup** - Depends on root-level customer_support module
3. **Package manager lock files ignored** - Generate your own, then remove from .gitignore
4. **Windows path separators** - npm scripts use backslashes for `.venv\Scripts\python.exe`
