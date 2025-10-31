# Document Processing Pipeline

A production-grade document processing and retrieval system built with SOLID principles, featuring PDF extraction, embedding generation, and semantic search with reranking.

## Architecture

This pipeline follows **SOLID principles** for maintainable, testable, and extensible code:

- **Single Responsibility**: Each class has one job (extractor, chunker, embedder, etc.)
- **Open/Closed**: Easy to extend with new extractors or embedders without modifying existing code
- **Liskov Substitution**: All implementations follow their interfaces
- **Interface Segregation**: Clean interfaces for each component
- **Dependency Injection**: Components receive dependencies via constructors

### Components

```
Document (PDF) → Extractor → Chunker → Embedder → Vector DB
                                                        ↓
User Query → Embedder → Vector Search → Reranker → Results
```

1. **DoclingExtractor** - Extracts text from PDFs using Docling
2. **OverlapTextChunker** - Splits documents into overlapping chunks
3. **NvidiaEmbeddingGenerator** - Generates embeddings using NVIDIA API
4. **QdrantVectorDB** - Stores and searches embeddings
5. **NvidiaReranker** - Reranks results for better relevance
6. **RetrievalPipeline** - Orchestrates search with reranking

## Setup

### 1. Install Dependencies

```bash
cd document_pipeline
pip install -r requirements.txt
```

### 2. Start Qdrant

```bash
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your NVIDIA API key:

```bash
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY
```

## Usage

### Process Documents

Extract and index all PDFs in a directory:

```bash
python main.py process ../Data
```

This will:
1. Extract text from all PDFs using Docling
2. Split into chunks (512 tokens, 50 token overlap)
3. Generate embeddings for each chunk
4. Store in Qdrant vector database

### Search Documents

Search for documents matching a query:

```bash
python main.py search "retail compliance requirements"
```

This performs:
1. Query embedding generation
2. Vector search (top 50 candidates)
3. Reranking (top 10 results)

### Interactive Mode

Start an interactive search session:

```bash
python main.py interactive
```

## NVIDIA Models Used

### Embeddings: `nvidia/llama-3.2-nemoretriever-300m-embed-v2`
- 2048-dimensional vectors (300M refers to model parameters, not embedding dims)
- 8192 token limit
- Supports both query and passage modes

### Reranker: `nvidia/llama-3.2-nv-rerankqa-1b-v2`
- Cross-attention between query and documents
- Significantly improves precision
- Use after vector search for top-k refinement

## Code Structure

```
Customer_support/Code/document_pipeline/
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── interfaces.py              # Abstract base classes
├── extractor.py               # PDF extraction (Docling)
├── chunker.py                 # Text chunking with overlap
├── embedding_generator.py     # NVIDIA embeddings
├── vector_db.py               # Qdrant operations
├── reranker.py                # NVIDIA reranker
├── retrieval_pipeline.py      # Search orchestration
├── document_processor.py      # Processing orchestration
└── requirements.txt           # Dependencies
```

## Example: Extending the System

### Add a new extractor (e.g., for Word docs):

```python
from interfaces import IDocumentExtractor, Document

class WordExtractor(IDocumentExtractor):
    async def extract(self, file_path: str) -> List[Document]:
        # Your implementation
        pass

# Use it:
extractor = WordExtractor()  # Instead of DoclingExtractor()
processor = DocumentProcessor(extractor, chunker, embedder, vector_db)
```

### Add a custom chunker:

```python
from interfaces import ITextChunker, Document, DocumentChunk

class SemanticChunker(ITextChunker):
    def chunk(self, document: Document) -> List[DocumentChunk]:
        # Your implementation
        pass
```

## Configuration

All configuration is in `.env`:

- `NVIDIA_API_KEY` - Your NVIDIA API key (required)
- `QDRANT_URL` - Qdrant server URL
- `COLLECTION_NAME` - Vector collection name
- `CHUNK_SIZE` - Words per chunk (default: 512)
- `CHUNK_OVERLAP` - Overlap between chunks (default: 50)
- `INITIAL_TOP_K` - Candidates for reranking (default: 50)
- `RERANK_TOP_K` - Final results (default: 10)

## Testing

Run tests:

```bash
pytest tests/ -v
```

## Logging

Logs are written to:
- `logs/document_pipeline.log` - File log
- Console - Real-time output

## Performance Tips

1. **Batch Processing**: Process multiple files in parallel
2. **Caching**: Cache embeddings for frequently accessed documents
3. **Incremental Updates**: Only process new/changed documents
4. **Reranking**: Use for precision, skip for speed

## Troubleshooting

### "Import could not be resolved"
Install dependencies: `pip install -r requirements.txt`

### "NVIDIA_API_KEY is required"
Set your API key in `.env` file

### "Collection not found"
Run processing first: `python main.py process <directory>`

### "No results found"
1. Check if documents are processed
2. Try broader queries
3. Reduce `SCORE_THRESHOLD`

## License

MIT
