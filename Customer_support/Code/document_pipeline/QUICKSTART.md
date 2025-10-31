# Quick Start Guide

## 5-Minute Setup

### 1. Start Qdrant (Vector Database)

```bash
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant
```

### 2. Install Dependencies

```bash
cd Customer_support/Code/document_pipeline
pip install -r requirements.txt
```

### 3. Configure API Key

The `.env` file is already configured with your NVIDIA API key. Verify it:

```bash
cat .env
```

Should show:
```
NVIDIA_API_KEY=nvapi-3btsbNpe...
```

### 4. Process PDFs

Index all PDFs from the Data directory:

```bash
python main.py process ../Data
```

This will:
- Extract text from 4 PDF files
- Create ~100-500 chunks per file
- Generate embeddings for each chunk
- Store in Qdrant

Expected output:
```
Processing: RegulatedProductsHandbook.pdf
Step 1/4: Extracting text from PDF...
✓ Extracted 15 document(s)
Step 2/4: Chunking documents...
✓ Created 342 chunks
Step 3/4: Generating embeddings...
✓ Generated 342 embeddings
Step 4/4: Storing in vector database...
✓ Successfully stored in database
```

### 5. Search Documents

Try a search query:

```bash
python main.py search "retail compliance requirements"
```

Expected output:
```
SEARCH RESULTS (Top 10)

Result 1:
  Score: 0.8723
  Source: ../Customer_support/Data/Retail Program Standards Policy Statement July 2028.pdf
  Page: 3
  Content: The retail program must comply with all federal, state, and local regulations...

Result 2:
  Score: 0.8456
  Source: ../Customer_support/Data/RegulatedProductsHandbook.pdf
  Page: 12
  Content: Compliance requirements include proper labeling, documentation, and...
```

### 6. Interactive Search

For continuous searching:

```bash
python main.py interactive
```

```
Collection: customer_support_docs
Documents: 1247

Enter your search queries (type 'quit' to exit):

Query: product safety standards
Searching...

Found 10 results:

1. [0.876] ../Customer_support/Data/RegulatedProductsHandbook.pdf
   Page 8
   Product safety standards require adherence to...

Query: environmental regulations
Searching...

Found 8 results:

1. [0.891] ../Customer_support/Data/tclc-fs-fedreg-retail-environ-2012.pdf
   Page 5
   Environmental compliance standards mandate...
```

## Architecture Overview

```
PDF Files → Docling Extractor → Text Chunks → NVIDIA Embeddings → Qdrant DB
                                                                      ↓
User Query → NVIDIA Embeddings → Vector Search → NVIDIA Reranker → Results
```

## Key Features

✅ **SOLID Principles** - Clean, maintainable code  
✅ **Dependency Injection** - Easy to test and extend  
✅ **Async/Await** - High performance  
✅ **Two-Stage Retrieval** - Vector search + Reranking  
✅ **Production Ready** - Error handling, logging, validation  

## Common Commands

```bash
# Process all PDFs in a directory
python main.py process ../Data

# Search for specific information
python main.py search "environmental compliance"

# Interactive search mode
python main.py interactive

# Run examples
python examples.py
```

## Next Steps

1. **Integrate with AI Agent**: Use the retrieval pipeline in `nvdia-ag-ui/agent/agent.py`
2. **Add More Documents**: Drop PDFs in `Customer_support/Data/` and reprocess
3. **Customize Chunking**: Modify `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`
4. **Tune Retrieval**: Adjust `INITIAL_TOP_K` and `RERANK_TOP_K` for speed/accuracy trade-off

## Troubleshooting

### Collection not found
Run processing first: `python main.py process ../Data`

### "No results found"
- Check if documents are processed: Visit http://localhost:6333/dashboard
- Try broader queries
- Lower `SCORE_THRESHOLD` in `.env`

### Import errors
Install dependencies: `pip install -r requirements.txt`

### Qdrant not running
Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`

## Performance Tips

- **Initial indexing**: ~30-60 seconds per PDF
- **Search queries**: ~2-3 seconds with reranking
- **Batch processing**: Process multiple PDFs in parallel
- **Skip reranking**: Use `use_reranking=False` for 10x faster search

## Support

Check logs in `logs/document_pipeline.log` for detailed information.
