# Customer Support Agent

An intelligent customer support agent that provides accurate, document-grounded answers to retail policy and compliance questions using NVIDIA's RAG (Retrieval-Augmented Generation) pipeline.

## 🎯 Overview

The Customer Support Agent leverages NVIDIA's advanced embedding and reranking models combined with Qdrant vector database to search through retail policy documents and provide accurate, cited responses to customer inquiries.

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│              Customer Support Agent                  │
│              (Google ADK + Gemini)                   │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│ Tools Module    │    │ Retrieval        │
│ - search_docs   │───▶│ Pipeline         │
│ - get_info      │    │ (NVIDIA + Qdrant)│
└─────────────────┘    └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌─────────────┐
            │ NVIDIA API   │    │ Qdrant DB   │
            │ - Embeddings │    │ - Vectors   │
            │ - Reranking  │    │ - Metadata  │
            └──────────────┘    └─────────────┘
```

### Technology Stack

- **Agent Framework**: Google ADK (Agent Development Kit)
- **LLM**: Gemini 2.0 Flash
- **Embedding Model**: NVIDIA `llama-3.2-nemoretriever-300m-embed-v2` (2048-dim)
- **Reranker Model**: NVIDIA `llama-3.2-nv-rerankqa-1b-v2`
- **Vector Database**: Qdrant (cosine similarity)
- **Backend**: Python FastAPI (async)
- **Frontend**: Next.js 15 + CopilotKit

## 🚀 Features

### 1. Semantic Policy Search
- **Natural Language Queries**: Ask questions in plain English
- **Document Retrieval**: Search through indexed policy documents
- **Source Citations**: Every answer includes source document and location
- **Confidence Scores**: Transparency in answer quality

### 2. Advanced RAG Pipeline
- **Vector Embeddings**: Convert queries to 2048-dimensional vectors
- **Similarity Search**: Cosine distance for semantic matching
- **Neural Reranking**: Second-stage refinement for accuracy
- **Multi-stage Retrieval**: 
  1. Initial search (top 20 candidates)
  2. Rerank with neural model
  3. Return top 5 most relevant

### 3. Collection Management
- **Database Status**: Check collection health
- **Document Count**: Total indexed chunks
- **Metadata Tracking**: Source files, timestamps, chunk info

## 📋 Prerequisites

### Environment Variables

Create a `.env` file in the `customer_support/` directory:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxx
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
NVIDIA_RERANK_URL=https://integrate.api.nvidia.com/v1/ranking

# Model Configuration
EMBEDDING_MODEL=nvidia/llama-3.2-nemoretriever-300m-embed-v2
RERANK_MODEL=nvidia/llama-3.2-nv-rerankqa-1b-v2

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=customer_support_docs
EMBEDDING_DIM=2048

# Processing Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
BATCH_SIZE=10
REQUEST_TIMEOUT=60
```

### Required Services

1. **Qdrant Vector Database**
   ```bash
   docker run -d -p 6333:6333 -p 6334:6334 \
     -v qdrant_storage:/qdrant/storage \
     --name qdrant qdrant/qdrant
   ```

2. **NVIDIA API Key**
   - Sign up at [NVIDIA Developer Portal](https://build.nvidia.com/)
   - Get API key from integrate.api.nvidia.com
   - Must start with `nvapi-`

## 🛠️ Setup & Installation

### 1. Process Policy Documents

First, index your retail policy documents:

```bash
cd customer_support
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Process PDFs from Data directory
python main.py process ./data
```

This will:
- Extract text from PDFs using Docling
- Chunk documents (512 tokens, 50 overlap)
- Generate embeddings with NVIDIA API
- Store in Qdrant collection

### 2. Install Agent Dependencies

```bash
cd nvdia-ag-ui
npm install  # Installs UI + agent dependencies
```

### 3. Run the Application

```bash
npm run dev
```

This starts:
- **Frontend**: http://localhost:3000
- **Agent Backend**: http://localhost:8000

## 📖 Usage

### In the UI

1. Navigate to http://localhost:3000
2. Select "Customer Support Agent" from sidebar
3. Ask policy questions:
   - "What is your return policy?"
   - "Can I return electronics without a receipt?"
   - "What's the warranty period for appliances?"
   - "Do you accept returns on sale items?"

### Example Interaction

**User**: "What is your return policy for electronics?"

**Agent Response**:
```
**Return Policy for Electronics**:

According to our Returns and Exchanges Policy (chunk 5):
"Electronic items may be returned within 30 days of purchase with original 
packaging, accessories, and proof of purchase. Items must be in new, unused 
condition."

**Additional Details**:
- Restocking fee: 15% for opened electronics
- Warranty items: Different process applies
- Receipt required for all returns

**Confidence**: 0.92/1.0 (Rerank Score)
**Source**: Returns_Policy_2024.pdf, Section 3.2
```

## 🔧 Tools Available

### 1. `search_policy_documents`

Main tool for answering customer questions.

**Parameters**:
- `query` (str, required): The customer's question
- `top_k` (int, optional): Number of results (default: 5)

**Returns**:
```python
{
    "success": True,
    "query": "What is the return policy?",
    "results_count": 5,
    "results": [
        {
            "rank": 1,
            "text": "Policy text content...",
            "source_filename": "Returns_Policy_2024.pdf",
            "chunk_index": 5,
            "similarity_score": 0.89,
            "rerank_score": 0.92,
            "metadata": {...}
        }
    ]
}
```

### 2. `get_collection_info`

Check database status and statistics.

**Parameters**: None

**Returns**:
```python
{
    "success": True,
    "collection_name": "customer_support_docs",
    "total_chunks": 1247,
    "status": "green",
    "vector_size": 2048
}
```

## 📊 Response Quality Metrics

### Similarity Scores

**Vector Similarity** (0.0 - 1.0):
- Initial cosine similarity from Qdrant search
- Higher = more semantically similar

**Rerank Score** (continuous):
- Neural reranker confidence
- More accurate than vector similarity alone

### Score Interpretation

| Rerank Score | Confidence | Meaning |
|--------------|-----------|---------|
| > 0.8 | High | Direct, accurate answer |
| 0.6 - 0.8 | Good | Relevant context |
| 0.4 - 0.6 | Medium | Partial match |
| < 0.4 | Low | May not fully answer |

## 🔍 How It Works

### Retrieval Pipeline

1. **Query Processing**
   ```python
   query = "What is the return policy?"
   query_embedding = nvidia_api.embed(query, input_type="query")
   # Result: [2048 float values]
   ```

2. **Vector Search**
   ```python
   candidates = qdrant.search(
       vector=query_embedding,
       limit=20,
       score_threshold=None
   )
   # Returns: Top 20 similar document chunks
   ```

3. **Neural Reranking**
   ```python
   reranked = nvidia_reranker.rerank(
       query=query,
       passages=[c["text"] for c in candidates],
       top_k=5
   )
   # Returns: Top 5 after refinement
   ```

4. **Response Generation**
   - Agent receives ranked results with metadata
   - Gemini 2.0 generates natural language answer
   - Includes citations and confidence scores

## 🗂️ Document Structure

### Qdrant Point Format

```python
{
    "id": 12345,
    "vector": [2048 floats],
    "payload": {
        "text": "Policy content...",
        "chunk_id": "doc_001_chunk_005",
        "chunk_index": 5,
        "source_filename": "Returns_Policy_2024.pdf",
        "source_filepath": "/data/Returns_Policy_2024.pdf",
        "char_count": 487,
        "metadata": {
            "document_type": "policy",
            "version": "2024.1",
            "department": "customer_service"
        },
        "inserted_at": "2024-11-01T10:30:00Z"
    }
}
```

## 🧪 Testing

### Test Tool Functions

```python
# Test in Python directly
from customer_support_agent.tools import search_policy_documents, get_collection_info

# Search test
result = search_policy_documents(
    query="What is the return policy?",
    top_k=3
)
print(result)

# Collection info test
info = get_collection_info()
print(info)
```

### Test Agent via API

```bash
# Health check
curl http://localhost:8000/health

# Test through CopilotKit endpoint
curl -X POST http://localhost:3000/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is your return policy?"}
    ]
  }'
```

## 🔐 Best Practices

### For Policy Documents

1. **Clear Structure**: Use headers, sections, bullet points
2. **Version Control**: Include version numbers in filenames
3. **Consistent Naming**: Use descriptive file names
4. **Regular Updates**: Re-process when policies change
5. **Metadata**: Include document type, department, date

### For Queries

1. **Be Specific**: "electronics return policy" > "returns"
2. **Use Keywords**: Include product categories, time periods
3. **Natural Language**: Full questions work best
4. **Context**: Provide relevant details

### For Responses

1. **Always Cite**: Include source document and location
2. **Show Confidence**: Display similarity/rerank scores
3. **Be Transparent**: Clearly state when unsure
4. **Provide Options**: Suggest related searches

## 🐛 Troubleshooting

### No Results Found

**Possible Causes**:
1. Documents not indexed yet
2. Query too specific or uses uncommon terms
3. Collection name mismatch

**Solutions**:
```bash
# Check collection exists
curl http://localhost:6333/collections

# Verify documents indexed
python -c "from tools import get_collection_info; print(get_collection_info())"

# Re-process documents
cd customer_support
python main.py process ./data
```

### Low Confidence Scores

**Causes**:
- Query-document semantic mismatch
- Documents lack detail on topic
- Chunking issues

**Solutions**:
- Rephrase query with different keywords
- Add more comprehensive policy documents
- Adjust chunk size in config

### API Errors

**NVIDIA API**:
```bash
# Test API key
curl -H "Authorization: Bearer $NVIDIA_API_KEY" \
  https://integrate.api.nvidia.com/v1/embeddings
```

**Qdrant Connection**:
```bash
# Test Qdrant
curl http://localhost:6333/collections
```

## 📚 Related Documentation

- [NVIDIA NeMo Retriever](https://build.nvidia.com/nvidia/nemo-retriever)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Google ADK Guide](https://ai.google.dev/adk)
- [CopilotKit Docs](https://docs.copilotkit.ai/)

## 🤝 Contributing

When adding new features:

1. Follow SOLID principles (see main copilot-instructions.md)
2. Use dependency injection for configs
3. Add logging for debugging
4. Include docstrings with examples
5. Test with sample policy documents

## 📝 License

Part of NVIDIA Retail AI Teams project.

---

**Need Help?**
- Check logs in `customer_support/logs/`
- Verify Qdrant collection at http://localhost:6333
- Test NVIDIA API key validity
- Ensure documents are processed and indexed
