# Customer Support Document Pipeline - README

## Overview

Complete document ingestion and retrieval pipeline for customer support PDFs using:
- **Docling** for OCR and text extraction
- **Recursive chunking** for intelligent text splitting
- **NVIDIA embeddings** (llama-3.2-nv-embedqa-1b-v2) for semantic search
- **Qdrant** vector database for storage
- **NVIDIA reranker** (llama-3.2-nv-rerankqa-1b-v2) for result refinement

## Architecture

```
PDF Files (Data/)
    ↓
Docling Extractor (OCR + Structure)
    ↓
Recursive Chunker (512 tokens, 50 overlap)
    ↓
NVIDIA Embeddings (2048-dim vectors)
    ↓
Qdrant Vector DB (cosine similarity)
    ↓
Query → Embed → Search (top 20) → Rerank (top 5) → Results
```

## Setup

### 1. Install Dependencies

```bash
cd Customer_support/Code/document_pipeline
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Start Qdrant

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  --name qdrant qdrant/qdrant
```

Verify: http://localhost:6333/dashboard

### 3. Configure Environment

The `.env` file is already configured with:
- NVIDIA API key
- Embedding model: nvidia/llama-3.2-nv-embedqa-1b-v2
- Reranker model: nvidia/llama-3.2-nv-rerankqa-1b-v2
- Chunk size: 512 tokens
- Top-K: 20 candidates
- Rerank top-N: 5 results

## Usage

### Ingest Documents

Place PDF files in `Customer_support/Data/` folder, then run:

```bash
python main.py
```

This will:
1. Extract text from all PDFs using Docling OCR
2. Split text into 512-token chunks with 50-token overlap
3. Generate NVIDIA embeddings (2048-dim)
4. Store in Qdrant vector database
5. Run example search

### Search Documents

```bash
python tests/test_search.py
```

Choose test mode:
- **1**: Single query test (default CPSC query)
- **2**: Batch test (8 predefined queries)
- **3**: Custom query (enter your own)

## Test Queries

Based on CPSC (Consumer Product Safety Commission) text:

1. "What is the Consumer Product Safety Commission?"
2. "When was CPSC established?"
3. "What are the main responsibilities of the CPSC?"
4. "How many statutes does CPSC administer?"
5. "What types of consumer products does CPSC regulate?"
6. "What is the mission of the CPSC?"
7. "How does CPSC achieve its goals?"
8. "Is CPSC an independent federal agency?"

## Sample CPSC Document

Create a test PDF with this content in `Customer_support/Data/CPSC_Overview.pdf`:

```
U.S. Consumer Product Safety Commission Overview

The U.S. Consumer Product Safety Commission (CPSC or Commission), established 
by Congress in 1972, is an independent federal regulatory agency charged with 
reducing unreasonable risks of injury and death associated with consumer products.

The CPSC achieves that goal through education, safety standards activities, 
regulation, and enforcement of the statutes and implementing regulations.

The CPSC has jurisdiction over thousands of types of consumer products used in 
the home, in schools, in recreation, or otherwise.

To carry out its mission, CPSC administers seven statutes passed by Congress 
(the Acts). They are:
1. Consumer Product Safety Act (CPSA)
2. Federal Hazardous Substances Act (FHSA)
3. Flammable Fabrics Act (FFA)
4. Poison Prevention Packaging Act (PPPA)
5. Refrigerator Safety Act (RSA)
6. Virginia Graeme Baker Pool and Spa Safety Act (VGB Act)
7. Children's Gasoline Burn Prevention Act (CGBPA)

The Commission works to ensure that consumer products are safe for families 
and individuals across the United States.
```

## Project Structure

```
Customer_support/
├── Code/
│   └── document_pipeline/
│       ├── .env                          # Configuration
│       ├── requirements.txt              # Dependencies
│       ├── config.py                     # Config management
│       ├── interfaces.py                 # Abstract interfaces
│       ├── extractor.py                  # Docling OCR extractor
│       ├── chunker.py                    # Recursive text chunker
│       ├── embedding_generator.py        # NVIDIA embeddings
│       ├── vector_db.py                  # Qdrant operations
│       ├── reranker.py                   # NVIDIA reranker
│       ├── retrieval_pipeline.py         # End-to-end search
│       ├── main.py                       # Ingestion pipeline
│       ├── logs/                         # Pipeline logs
│       └── tests/
│           └── test_search.py            # Search tests
└── Data/                                 # Place PDF files here
    └── [your-pdfs].pdf
```

## API Reference

### Configuration (config.py)

```python
config = Config.from_env()
config.validate()

# Access settings
config.nvidia.api_key
config.nvidia.embedding_model
config.nvidia.reranker_model
config.qdrant.url
config.qdrant.collection_name
config.processing.chunk_size
config.retrieval.top_k
config.retrieval.rerank_top_n
```

### Document Extraction

```python
from extractor import DoclingExtractor

extractor = DoclingExtractor()
text = extractor.extract("path/to/document.pdf")
doc_data = extractor.extract_with_metadata("path/to/document.pdf")
```

### Text Chunking

```python
from chunker import RecursiveChunker

chunker = RecursiveChunker(chunk_size=512, chunk_overlap=50)
chunks = chunker.chunk(text, metadata={"source": "doc.pdf"})
```

### Embedding Generation

```python
from embedding_generator import NvidiaEmbeddingGenerator

embedder = NvidiaEmbeddingGenerator(
    api_key="your-key",
    model="nvidia/llama-3.2-nv-embedqa-1b-v2"
)

# For documents
doc_embeddings = embedder.generate_embeddings(texts)

# For queries
query_embedding = embedder.generate_query_embedding(query)
```

### Vector Database

```python
from vector_db import QdrantVectorDB

db = QdrantVectorDB(
    url="http://localhost:6333",
    collection_name="customer_support_docs",
    vector_size=2048
)

db.create_collection()
db.upsert_documents(documents)
results = db.search(query_embedding, top_k=20)
```

### Reranking

```python
from reranker import NvidiaReranker

reranker = NvidiaReranker(
    api_key="your-key",
    model="nvidia/llama-3.2-nv-rerankqa-1b-v2"
)

reranked = reranker.rerank(query, documents, top_n=5)
```

### Complete Pipeline

```python
from retrieval_pipeline import RetrievalPipeline

pipeline = RetrievalPipeline(
    embedding_generator=embedder,
    vector_db=db,
    reranker=reranker,
    config=retrieval_config
)

results = pipeline.search("your query")
```

## Logging

Logs are written to:
- `logs/pipeline.log` - Pipeline execution logs
- Console output - Real-time progress

## Troubleshooting

### Qdrant Connection Error
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker restart qdrant
```

### NVIDIA API Errors
- Verify API key in `.env`
- Check rate limits: https://build.nvidia.com/
- Ensure models are available in your region

### Empty Search Results
- Check if documents were ingested: `collection_exists()`
- Verify embedding dimensions match (2048)
- Lower `SCORE_THRESHOLD` in `.env`

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Performance Tips

1. **Batch Processing**: Adjust `BATCH_SIZE` in `.env` (default: 10)
2. **Concurrent Processing**: Modify batch size in `embed_documents_batch()`
3. **Chunk Size**: Larger chunks (1024) = fewer vectors, faster search
4. **Top-K**: Higher TOP_K (50) = better recall, slower reranking

## References

- **Docling**: https://github.com/DS4SD/docling
- **NVIDIA AI**: https://build.nvidia.com/
- **Qdrant**: https://qdrant.tech/documentation/
- **LangChain**: https://python.langchain.com/

## License

MIT License - See project root for details
