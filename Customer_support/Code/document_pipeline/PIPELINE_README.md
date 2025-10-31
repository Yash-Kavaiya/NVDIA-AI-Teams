# Customer Support Document Pipeline

Complete data ingestion and retrieval pipeline for PDF documents using:
- **Docling** for OCR and text extraction
- **Recursive Chunking** for intelligent text splitting
- **NVIDIA Embeddings** (llama-3.2-nv-embedqa-1b-v2) for semantic search
- **Qdrant** vector database for storage
- **NVIDIA Reranker** (llama-3.2-nv-rerankqa-1b-v2) for result refinement

## 🏗️ Architecture

```
PDFs → Docling OCR → Recursive Chunking (512/50) → 
NVIDIA Embeddings (2048-dim) → Qdrant Storage →
Query → Embed → Vector Search (top 20) → Rerank (top 5) → Results
```

## 📋 Prerequisites

1. **Python 3.8+**
2. **Docker** (for Qdrant)
3. **NVIDIA API Key** (already configured in .env)

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
cd Customer_support\Code\document_pipeline
pip install -r requirements.txt
```

### 2. Start Qdrant Vector Database

```powershell
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
```

Verify Qdrant is running: http://localhost:6333/dashboard

### 3. Create Test PDF (Optional)

```powershell
python create_test_pdf.py
```

This creates `../../Data/CPSC_Overview.pdf` with CPSC text content.

Or add your own PDFs to `Customer_support/Data/` folder.

### 4. Run Ingestion Pipeline

```powershell
python main.py
```

This will:
- ✅ Extract text from all PDFs in Data folder
- ✅ Chunk documents (512 tokens, 50 overlap)
- ✅ Generate embeddings using NVIDIA API
- ✅ Store in Qdrant vector database

### 5. Test Retrieval

```powershell
cd tests
python test_search.py
```

Choose test mode:
- **1**: Single query test
- **2**: Batch test (all 8 CPSC queries)
- **3**: Custom query (enter your own)

## 📁 Project Structure

```
document_pipeline/
├── config.py              # Configuration management
├── interfaces.py          # Abstract base classes
├── extractor.py          # Docling OCR extractor
├── chunker.py            # Recursive text splitter
├── embedding_generator.py # NVIDIA embeddings
├── vector_db.py          # Qdrant operations
├── reranker.py           # NVIDIA reranker
├── retrieval_pipeline.py # Search orchestration
├── main.py               # Ingestion pipeline
├── create_test_pdf.py    # Generate test PDF
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── tests/
│   └── test_search.py   # Search tests
└── logs/
    └── pipeline.log     # Execution logs
```

## 🔧 Configuration

All settings in `.env`:

```env
# NVIDIA API
NVIDIA_API_KEY=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
EMBEDDING_MODEL=nvidia/llama-3.2-nv-embedqa-1b-v2
RERANKER_MODEL=nvidia/llama-3.2-nv-rerankqa-1b-v2

# Qdrant
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=customer_support_docs
EMBEDDING_DIM=2048

# Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
BATCH_SIZE=10

# Retrieval
TOP_K=20              # Vector search candidates
RERANK_TOP_N=5        # Final results
SCORE_THRESHOLD=0.3   # Minimum similarity
```

## 🧪 Test Queries

The test suite includes 8 CPSC-based queries:

1. "What is the Consumer Product Safety Commission?"
2. "When was CPSC established?"
3. "What is the mission of CPSC?"
4. "How does CPSC achieve its goals?"
5. "What types of products does CPSC have jurisdiction over?"
6. "What statutes does CPSC administer?"
7. "What is the Consumer Product Safety Act?"
8. "How does CPSC regulate consumer products?"

## 📊 Example Usage

### Ingestion

```python
from config import Config
from main import DocumentPipeline

# Load config
config = Config.from_env()

# Create pipeline
pipeline = DocumentPipeline(config)

# Process all PDFs
num_chunks = pipeline.process_documents(config.data_dir)
print(f"Processed {num_chunks} chunks")
```

### Search

```python
from config import Config
from retrieval_pipeline import RetrievalPipeline

# Initialize
config = Config.from_env()
retrieval = RetrievalPipeline(...)

# Search
query = "What is CPSC?"
results = retrieval.search(query)

# Display
for result in results:
    print(f"Score: {result.score:.4f}")
    print(f"Content: {result.document.content}")
```

## 🔍 How It Works

### 1. Document Extraction (Docling)
- Extracts text from PDFs with OCR support
- Preserves document structure (headings, paragraphs)
- Handles tables and images

### 2. Recursive Chunking
- Splits text at natural boundaries (paragraphs → sentences → words)
- 512 token chunks with 50 token overlap
- Preserves context across chunk boundaries

### 3. Embedding Generation (NVIDIA)
- Uses `nvidia/llama-3.2-nv-embedqa-1b-v2` model
- 2048-dimensional dense vectors
- Batch processing for efficiency

### 4. Vector Storage (Qdrant)
- Cosine similarity search
- Metadata preserved for each chunk
- Fast approximate nearest neighbor search

### 5. Reranking (NVIDIA)
- Uses `nvidia/llama-3.2-nv-rerankqa-1b-v2` model
- Refines top-k results from vector search
- Cross-encoder for better relevance

## 🐛 Troubleshooting

### Docling Import Error
```
ModuleNotFoundError: No module named 'docling'
```
**Solution**: `pip install docling`

### Qdrant Connection Error
```
ConnectionRefusedError: [Errno 61] Connection refused
```
**Solution**: Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`

### NVIDIA API Error
```
AuthenticationError: Invalid API key
```
**Solution**: Check `.env` file has correct `NVIDIA_API_KEY`

### Empty Search Results
```
Found 0 results
```
**Solution**: 
1. Check collection exists: http://localhost:6333/dashboard
2. Run ingestion: `python main.py`
3. Verify PDFs in `../../Data/` folder

## 📈 Performance Tips

1. **Batch Processing**: Adjust `BATCH_SIZE` in .env (default: 10)
2. **Chunk Size**: Larger chunks = more context, fewer chunks (default: 512)
3. **Top-K**: More candidates = better recall (default: 20)
4. **Score Threshold**: Higher = stricter filtering (default: 0.3)

## 🔗 References

- [Docling Documentation](https://github.com/DS4SD/docling)
- [NVIDIA AI Endpoints](https://build.nvidia.com/explore/discover)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)
- [LangChain](https://python.langchain.com/docs/get_started/introduction)

## 📝 License

Part of NVIDIA AI Teams project.

---

**Need Help?** Check logs at `logs/pipeline.log` for detailed execution information.
