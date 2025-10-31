# Testing & Validation Checklist

## Pre-Flight Checks

### Environment Setup
- [ ] Docker installed and running
- [ ] Python 3.8+ installed
- [ ] Qdrant container running on port 6333
- [ ] NVIDIA API key configured in `.env`
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### Configuration Validation
```bash
cd Customer_support/Code/document_pipeline
python -c "from config import Config; c = Config.from_env(); c.validate(); print('✓ Config valid')"
```

Expected: `✓ Config valid`

### Qdrant Connection
```bash
curl http://localhost:6333/collections
```

Expected: JSON response with collections list

## Component Testing

### 1. PDF Extraction (Docling)

Test single PDF extraction:

```bash
cd Customer_support/Code/document_pipeline
python -c "
import asyncio
from extractor import DoclingExtractor

async def test():
    extractor = DoclingExtractor()
    docs = await extractor.extract('../Data/RegulatedProductsHandbook.pdf')
    print(f'✓ Extracted {len(docs)} pages')
    print(f'✓ First page has {len(docs[0].content.split())} words')

asyncio.run(test())
"
```

Expected:
```
✓ Extracted 15 pages
✓ First page has 342 words
```

### 2. Text Chunking

Test chunking logic:

```bash
python -c "
from config import Config, DocumentProcessingConfig
from chunker import OverlapTextChunker
from interfaces import Document

config = DocumentProcessingConfig(chunk_size=100, chunk_overlap=20, batch_size=10)
chunker = OverlapTextChunker(config)

doc = Document(
    content=' '.join([f'word{i}' for i in range(250)]),
    metadata={},
    source='test.pdf'
)

chunks = chunker.chunk(doc)
print(f'✓ Created {len(chunks)} chunks')
print(f'✓ First chunk: {len(chunks[0].content.split())} words')
print(f'✓ Overlap preserved: {chunks[0].content.split()[-5:] == chunks[1].content.split()[:5]}')
"
```

Expected:
```
✓ Created 3 chunks
✓ First chunk: 100 words
✓ Overlap preserved: True
```

### 3. Embedding Generation

Test NVIDIA embeddings:

```bash
python -c "
import asyncio
from config import Config
from embedding_generator import NvidiaEmbeddingGenerator

async def test():
    config = Config.from_env()
    generator = NvidiaEmbeddingGenerator(config.nvidia)
    
    embedding = await generator.generate_embedding('test query', input_type='query')
    print(f'✓ Generated embedding with {len(embedding)} dimensions')
    print(f'✓ Embedding type: {type(embedding[0])}')

asyncio.run(test())
"
```

Expected:
```
✓ Generated embedding with 300 dimensions
✓ Embedding type: <class 'float'>
```

### 4. Vector Database

Test Qdrant operations:

```bash
python -c "
import asyncio
from config import Config
from vector_db import QdrantVectorDB
from interfaces import DocumentChunk

async def test():
    config = Config.from_env()
    db = QdrantVectorDB(config.qdrant)
    
    await db.create_collection()
    print('✓ Collection created/exists')
    
    info = db.get_collection_info()
    print(f'✓ Collection info: {info}')

asyncio.run(test())
"
```

Expected:
```
✓ Collection created/exists
✓ Collection info: {'name': 'customer_support_docs', 'vectors_count': 0, 'points_count': 0, 'status': 'green'}
```

### 5. Reranker

Test NVIDIA reranker:

```bash
python -c "
import asyncio
from config import Config
from reranker import NvidiaReranker
from interfaces import SearchResult

async def test():
    config = Config.from_env()
    reranker = NvidiaReranker(config.nvidia)
    
    results = [
        SearchResult(content='text about compliance', score=0.8, metadata={}, source='doc1.pdf'),
        SearchResult(content='text about retail', score=0.7, metadata={}, source='doc2.pdf'),
    ]
    
    reranked = await reranker.rerank('compliance requirements', results, top_k=2)
    print(f'✓ Reranked {len(reranked)} results')
    print(f'✓ Scores updated: {[r.score for r in reranked]}')

asyncio.run(test())
"
```

Expected:
```
✓ Reranked 2 results
✓ Scores updated: [0.923, 0.456]
```

## End-to-End Testing

### 1. Process Single PDF

```bash
cd Customer_support/Code/document_pipeline
python main.py process ../Data
```

**Expected Output:**
```
================================================================================
DOCUMENT PROCESSING PIPELINE
================================================================================
Found 4 PDF files to process

================================================================================
Processing: RegulatedProductsHandbook.pdf
================================================================================
Step 1/4: Extracting text from PDF...
✓ Extracted 15 document(s)
Step 2/4: Chunking documents...
✓ Created 342 chunks
Step 3/4: Generating embeddings...
✓ Generated 342 embeddings
Step 4/4: Storing in vector database...
✓ Successfully stored in database

[Repeat for other PDFs...]

================================================================================
PROCESSING COMPLETE
================================================================================
Total files: 4
Successful: 4
Failed: 0
Total chunks: 1247
Total embeddings: 1247
Duration: 178.45 seconds
================================================================================
```

**Validation Checks:**
- [ ] All PDFs processed successfully
- [ ] No failed files
- [ ] Reasonable chunk count (~200-400 per PDF)
- [ ] Processing time < 5 minutes

### 2. Basic Search

```bash
python main.py search "retail compliance requirements"
```

**Expected Output:**
```
================================================================================
DOCUMENT RETRIEVAL
================================================================================
Query: retail compliance requirements

================================================================================
SEARCH RESULTS (Top 10)
================================================================================

Result 1:
  Score: 0.8923
  Source: ../Customer_support/Data/RegulatedProductsHandbook.pdf
  Page: 12
  Content: Retail compliance requirements mandate that all retail establishments must adhere to federal, state, and local regulations...

Result 2:
  Score: 0.8756
  Source: ../Customer_support/Data/Retail Program Standards Policy Statement July 2028.pdf
  Page: 5
  Content: All retail operations must maintain compliance with applicable standards including...

[8 more results...]
```

**Validation Checks:**
- [ ] Returns 10 results
- [ ] Scores are between 0 and 1
- [ ] Results are relevant to query
- [ ] Page numbers present
- [ ] Sources are correct file paths

### 3. Interactive Search

```bash
python main.py interactive
```

**Test Queries:**
```
Query: product safety regulations
Query: environmental compliance
Query: labeling requirements
Query: retail standards
Query: quit
```

**Validation Checks:**
- [ ] All queries return results
- [ ] Results are relevant
- [ ] Can exit with 'quit'
- [ ] No crashes on empty queries

## Performance Testing

### Embedding Speed
```bash
python -c "
import asyncio
import time
from config import Config
from embedding_generator import NvidiaEmbeddingGenerator

async def test():
    config = Config.from_env()
    generator = NvidiaEmbeddingGenerator(config.nvidia)
    
    texts = ['test query ' + str(i) for i in range(10)]
    
    start = time.time()
    embeddings = await generator.generate_batch_embeddings(texts, 'passage')
    duration = time.time() - start
    
    print(f'✓ Generated {len(embeddings)} embeddings in {duration:.2f}s')
    print(f'✓ Average: {duration/len(embeddings):.2f}s per embedding')

asyncio.run(test())
"
```

**Expected:** < 2 seconds per embedding

### Search Speed
```bash
time python main.py search "compliance requirements"
```

**Expected:** 
- Without reranking: < 1 second
- With reranking: < 3 seconds

### Memory Usage
```bash
python -c "
import asyncio
import psutil
import os
from config import Config
from document_processor import DocumentProcessor
from extractor import DoclingExtractor
from chunker import OverlapTextChunker
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB

async def test():
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    config = Config.from_env()
    extractor = DoclingExtractor()
    chunker = OverlapTextChunker(config.processing)
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    
    processor = DocumentProcessor(extractor, chunker, embedder, vector_db)
    
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f'✓ Memory usage: {mem_after - mem_before:.2f} MB')

asyncio.run(test())
"
```

**Expected:** < 200 MB

## Error Handling Tests

### Invalid API Key
```bash
# Temporarily set invalid key
export NVIDIA_API_KEY="invalid_key"
python main.py search "test"
# Restore valid key
```

**Expected:** Graceful error message, not crash

### Missing Collection
```bash
# Delete collection
curl -X DELETE http://localhost:6333/collections/customer_support_docs

# Try search
python main.py search "test"
```

**Expected:** Error message: "Collection not found. Run processing first."

### Invalid PDF
```bash
echo "not a pdf" > /tmp/invalid.pdf
python -c "
import asyncio
from extractor import DoclingExtractor

async def test():
    extractor = DoclingExtractor()
    docs = await extractor.extract('/tmp/invalid.pdf')
    print(f'Extracted: {len(docs)} docs')

asyncio.run(test())
"
```

**Expected:** Error logged, returns empty list

## Integration Tests

### RAG Context Format
```bash
python -c "
import asyncio
from config import Config
from retrieval_pipeline import RetrievalPipeline
from embedding_generator import NvidiaEmbeddingGenerator
from vector_db import QdrantVectorDB
from reranker import NvidiaReranker

async def test():
    config = Config.from_env()
    embedder = NvidiaEmbeddingGenerator(config.nvidia)
    vector_db = QdrantVectorDB(config.qdrant)
    reranker = NvidiaReranker(config.nvidia)
    
    retrieval = RetrievalPipeline(embedder, vector_db, reranker, config.retrieval)
    response = await retrieval.retrieve_with_context('compliance', top_k=3)
    
    print(f'✓ Query: {response[\"query\"]}')
    print(f'✓ Results count: {response[\"results_count\"]}')
    print(f'✓ Has results: {len(response[\"results\"]) > 0}')
    print(f'✓ Reranked: {response[\"reranked\"]}')

asyncio.run(test())
"
```

**Expected:**
```
✓ Query: compliance
✓ Results count: 3
✓ Has results: True
✓ Reranked: True
```

## Final Validation

### Qdrant Dashboard
Visit: http://localhost:6333/dashboard

**Check:**
- [ ] Collection exists: `customer_support_docs`
- [ ] Points count > 1000
- [ ] Vectors dimension: 300
- [ ] Distance: Cosine

### Collection Statistics
```bash
python -c "
from config import Config
from vector_db import QdrantVectorDB

config = Config.from_env()
db = QdrantVectorDB(config.qdrant)
info = db.get_collection_info()

print('Collection Statistics:')
for key, value in info.items():
    print(f'  {key}: {value}')
"
```

**Expected:**
```
Collection Statistics:
  name: customer_support_docs
  vectors_count: 1247
  points_count: 1247
  status: green
```

## Success Criteria

✅ **All Components Working:**
- [ ] PDF extraction successful
- [ ] Chunking produces overlapping chunks
- [ ] Embeddings generated (300-dim)
- [ ] Qdrant stores and retrieves
- [ ] Reranker improves results

✅ **End-to-End Flow:**
- [ ] Can process all PDFs
- [ ] Can search documents
- [ ] Interactive mode works
- [ ] Results are relevant

✅ **Performance:**
- [ ] Processing: < 60s per PDF
- [ ] Search: < 3s with reranking
- [ ] Memory: < 500 MB

✅ **Code Quality:**
- [ ] No import errors
- [ ] Type hints throughout
- [ ] SOLID principles followed
- [ ] Error handling works
- [ ] Logging is clear

## Troubleshooting

### Issue: No results found
**Solution:** 
```bash
cd Customer_support/Code/document_pipeline
python main.py process ../Data
```

### Issue: Import errors
**Solution:** 
```bash
cd Customer_support/Code/document_pipeline
pip install -r requirements.txt
```

### Issue: Qdrant connection failed
**Solution:** 
```bash
docker ps  # Check if running
docker start qdrant  # Start if stopped
```

### Issue: NVIDIA API errors
**Solution:** Check API key in `.env`, verify at https://build.nvidia.com

## Next Steps After Validation

1. **Deploy to Production**
   - Containerize with Docker
   - Set up monitoring
   - Add API endpoints

2. **Integrate with AI Agent**
   - Import in `nvdia-ag-ui/agent/agent.py`
   - Add CopilotKit actions
   - Expose search via UI

3. **Optimize Performance**
   - Cache embeddings
   - Batch process PDFs
   - Add connection pooling

4. **Add Features**
   - OCR for scanned PDFs
   - Metadata filtering
   - Citation generation
   - Export results

---

**Test Status:** ☐ Not Started | ☑ Passed | ☒ Failed

**Last Updated:** 2025-10-31
