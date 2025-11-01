# Customer Support Agent - Quick Start Guide

Get your customer support agent up and running in 5 minutes!

## 🚀 Quick Setup

### Step 1: Start Qdrant Database

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  --name qdrant qdrant/qdrant
```

**Verify**: Open http://localhost:6333/dashboard

### Step 2: Configure Environment

Create `.env` in `customer_support/` directory:

```bash
# NVIDIA API Key (get from https://build.nvidia.com/)
NVIDIA_API_KEY=nvapi-your-key-here

# NVIDIA Endpoints
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings
NVIDIA_RERANK_URL=https://integrate.api.nvidia.com/v1/ranking

# Models
EMBEDDING_MODEL=nvidia/llama-3.2-nemoretriever-300m-embed-v2
RERANK_MODEL=nvidia/llama-3.2-nv-rerankqa-1b-v2

# Qdrant
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=customer_support_docs
EMBEDDING_DIM=2048

# Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
BATCH_SIZE=10
```

### Step 3: Process Documents

```bash
cd customer_support

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Process your PDF policy documents
python main.py process ./data
```

**What happens**:
- Extracts text from PDFs in `data/` folder
- Chunks into 512-token segments
- Generates NVIDIA embeddings (2048-dim)
- Stores in Qdrant `customer_support_docs` collection

**Expected Output**:
```
Processing documents from ./data
Found 5 PDF files
Processing: Returns_Policy_2024.pdf
- Extracted 42 chunks
- Generated embeddings
- Inserted into Qdrant
✅ Successfully processed 5 documents, 187 total chunks
```

### Step 4: Install UI Dependencies

```bash
cd nvdia-ag-ui
npm install
```

This installs:
- Next.js frontend packages
- CopilotKit SDK
- Python agent dependencies (via postinstall)

### Step 5: Run the Application

```bash
npm run dev
```

This starts:
- **Frontend**: http://localhost:3000
- **Agent Backend**: http://localhost:8000

### Step 6: Test the Agent

1. Open http://localhost:3000
2. Click "Customer Support Agent" in sidebar
3. Try these example queries:

```
"What is your return policy for electronics?"
"Can I return items without a receipt?"
"What is the warranty period for appliances?"
"Do you accept returns on sale items?"
```

**Expected Response Format**:
```
**Answer**: Electronics can be returned within 30 days...

**Supporting Policy**:
According to Returns_Policy_2024.pdf (chunk 5):
"Electronic items may be returned within 30 days..."

**Confidence**: 0.92/1.0
- Vector Similarity: 0.87
- Rerank Score: 0.92

**Source Document**: Returns_Policy_2024.pdf
```

## ✅ Verification Checklist

- [ ] Qdrant running on port 6333
- [ ] `.env` file configured with valid NVIDIA API key
- [ ] Documents processed and indexed
- [ ] Collection `customer_support_docs` exists in Qdrant
- [ ] UI running on http://localhost:3000
- [ ] Agent backend running on http://localhost:8000
- [ ] Agent responds to test queries

## 🧪 Test Your Setup

### Test 1: Verify Qdrant Collection

```bash
curl http://localhost:6333/collections/customer_support_docs
```

**Expected**: JSON with collection info, `points_count > 0`

### Test 2: Test Tools Directly

```bash
cd nvdia-ag-ui/agent
python customer_support_agent/test_agent.py
```

**Expected**: Search results with similarity scores and source documents

### Test 3: Test Agent API

```bash
curl -X POST http://localhost:3000/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is your return policy?"}
    ]
  }'
```

**Expected**: JSON response with agent's answer

## 🐛 Common Issues

### Issue: "Collection not found"

**Solution**:
```bash
cd customer_support
python main.py process ./data
```

### Issue: "NVIDIA API authentication failed"

**Solution**:
1. Check API key starts with `nvapi-`
2. Verify key at https://build.nvidia.com/
3. Check `.env` file location and format

### Issue: "No results found for query"

**Possible Causes**:
- Documents not indexed yet
- Query doesn't match document content
- Wrong collection name

**Solution**:
```python
# Check collection
from customer_support_agent.tools import get_collection_info
print(get_collection_info())
```

### Issue: Port already in use

**Solution**:
```bash
# Kill processes on ports
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

## 📊 Performance Tips

### For Better Search Results

1. **Add More Documents**: More comprehensive policy coverage
2. **Optimize Chunking**: Adjust `CHUNK_SIZE` (try 256, 512, 1024)
3. **Use Specific Queries**: "electronics return policy" > "returns"
4. **Include Metadata**: Add document type, version, department

### For Faster Response

1. **Reduce `top_k`**: Default is 5, try 3 for speed
2. **Skip Reranking**: Set `use_reranking=False` (less accurate)
3. **Batch Processing**: Process documents in parallel
4. **Qdrant Optimization**: Use SSD storage, increase memory

## 📚 Next Steps

1. **Add Your Documents**: Place PDFs in `customer_support/data/`
2. **Customize Agent**: Edit `agent.py` instruction prompt
3. **Add More Tools**: Extend `tools.py` with custom functions
4. **Improve UI**: Customize frontend in `src/components/`
5. **Deploy**: Use Vercel (frontend) + Railway/Render (backend)

## 🔗 Useful Links

- [Full README](./README.md) - Detailed documentation
- [NVIDIA API Docs](https://build.nvidia.com/nvidia/nemo-retriever)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [CopilotKit Guide](https://docs.copilotkit.ai/)

## 💡 Example Use Cases

1. **E-commerce Returns**: Answer return/exchange questions
2. **Warranty Claims**: Explain warranty coverage and process
3. **Shipping Policies**: Provide shipping options and costs
4. **Privacy Compliance**: Explain data handling policies
5. **Terms of Service**: Clarify user rights and responsibilities

## 🎯 Success Metrics

Monitor these to ensure quality:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Response Time | < 3s | Frontend timing |
| Rerank Score | > 0.7 | Tool output |
| Citations | 100% | Agent responses |
| User Satisfaction | > 4/5 | Feedback system |

---

**Need Help?**

1. Check logs: `customer_support/logs/`
2. Test tools: `python test_agent.py`
3. Verify Qdrant: http://localhost:6333/dashboard
4. Review `.env` configuration

**Ready to deploy?** See deployment guides in main README.
