# Product Search Agent - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you get the Product Search Agent up and running quickly.

## Prerequisites

- Python 3.8+
- Docker (for Qdrant)
- NVIDIA API key (from [build.nvidia.com](https://build.nvidia.com))
- Node.js 18+ (for UI)

## Step 1: Start Qdrant Vector Database

```powershell
# Start Qdrant using Docker
docker run -d -p 6333:6333 -p 6334:6334 `
  -v qdrant_storage:/qdrant/storage `
  --name qdrant `
  qdrant/qdrant

# Verify it's running
docker ps | findstr qdrant
```

Access Qdrant dashboard at: http://localhost:6333/dashboard

## Step 2: Configure Environment

Navigate to the image embeddings pipeline and create `.env`:

```powershell
cd ..\..\..\image_embeddings_pipeline
```

Create `.env` file (or copy from `.env.example`):

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1/embeddings

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=image_embeddings
EMBEDDING_DIM=4096

# Optional: Processing tuning
BATCH_SIZE=25
CONCURRENT_DOWNLOADS=10
CONCURRENT_EMBEDDINGS=5
IMAGE_MAX_SIZE=128
IMAGE_QUALITY=70
REQUEST_TIMEOUT=60
```

**Get your NVIDIA API key**: https://build.nvidia.com → Sign in → Get API Key

## Step 3: Install Dependencies & Index Products

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Index first 100 products (quick test)
python main.py 0 100

# Or index all products (takes longer)
# python main.py
```

**Expected output**:
```
✓ Connected to Qdrant at http://localhost:6333
✓ Created collection 'image_embeddings'
Processing images: 100%|████████████| 100/100
✓ Processed 100 images successfully
```

## Step 4: Verify Installation

```powershell
# Navigate to agent directory
cd ..\nvdia-ag-ui\agent\product_search_agent

# Run test suite
python test_agent.py
```

**Expected output**:
```
🎉 All tests passed! The Product Search Agent is ready to use.
```

## Step 5: Use the Agent

### Option A: Through UI (Recommended)

```powershell
# Navigate to UI directory
cd ..\..

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

Access at: http://localhost:3000

The Product Search Agent will be available in the chat interface.

### Option B: Direct Python Usage

```python
from product_search_agent import tools

# Text search
results = tools.search_products_by_text(
    query="red dress",
    limit=10,
    score_threshold=0.7
)

print(f"Found {results['results_count']} products:")
for item in results['results']:
    print(f"  - {item['filename']}: {item['similarity_score']}")

# Image search
results = tools.search_products_by_image(
    image_url="http://example.com/shoe.jpg",
    limit=5
)

# Collection stats
stats = tools.get_collection_stats()
print(f"Total products: {stats['total_products']}")
```

## 📝 Example Queries

Try these queries in the UI chat:

### Text Search Examples
```
"Find me red summer dresses"
"Show black leather boots"
"Search for casual men's sneakers"
"I need a formal watch"
"Show me denim jackets"
```

### Image Search Examples
```
"Find similar products to this image: [paste URL]"
"Show me products similar to http://assets.myntassets.com/..."
```

### Advanced Queries
```
"Search for red shoes added in the last week"
"Find leather bags with high similarity threshold"
"How many products are in the database?"
"Show me product details for ID 12345"
```

## 🔍 Understanding Results

### Similarity Scores

The agent returns similarity scores from 0.0 to 1.0:

- **0.9+** = Near-exact match (same or very similar item)
- **0.8-0.9** = Very similar (same category, close style)
- **0.7-0.8** = Similar (related items)
- **0.6-0.7** = Somewhat related
- **<0.6** = Low similarity

**Tip**: Use `score_threshold=0.7` for best results.

## 🐛 Troubleshooting

### "No results found"

**Check**:
1. Is Qdrant running? `docker ps`
2. Is collection indexed? `python test_agent.py`
3. Try broader query terms

### "Collection not found"

**Solution**: Index products first
```powershell
cd ..\..\..\image_embeddings_pipeline
python main.py 0 100
```

### "NVIDIA API error"

**Check**:
1. API key is valid (check .env)
2. API key format: `nvapi-...`
3. Internet connection works

### Import errors

**Solution**: Activate virtual environment
```powershell
cd ..\..\..\image_embeddings_pipeline
.\venv\Scripts\Activate.ps1
```

## 🎯 Next Steps

### 1. Index More Products

```powershell
cd image_embeddings_pipeline
python main.py 0 1000  # Index first 1000 products
```

### 2. Optimize Search

Adjust in code or through agent:
- Increase `score_threshold` for precision
- Increase `limit` for more results
- Use filters for targeted search

### 3. Integrate with Your UI

```typescript
// In your React component
import { useCopilotAction } from "@copilotkit/react-core";

useCopilotAction({
  name: "search_products",
  description: "Search for fashion products",
  parameters: [
    { name: "query", type: "string" }
  ],
  handler: async ({ query }) => {
    // Agent automatically handles this
  }
});
```

## 📊 Performance Tips

### For Faster Indexing
- Increase `CONCURRENT_DOWNLOADS` and `CONCURRENT_EMBEDDINGS` in .env
- Use smaller `IMAGE_MAX_SIZE` (faster processing, lower quality)

### For Better Search
- Be specific in queries ("red maxi dress" vs "dress")
- Use natural language descriptions
- Try different synonyms if no results

### For Large Catalogs
- Index in batches (e.g., 1000 at a time)
- Use filtered search to narrow results
- Consider increasing Qdrant resources

## 🔗 Resources

- **NVIDIA NIM Docs**: https://docs.nvidia.com/nim/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Full README**: See `README.md` in this directory
- **Architecture Guide**: See root `ARCHITECTURE.md`

## 💡 Pro Tips

1. **Cache frequently searched items** by storing popular queries
2. **Use image search** for "find similar" features
3. **Combine with inventory agent** for stock-aware recommendations
4. **Set score thresholds** based on use case:
   - Product discovery: 0.6-0.7
   - Exact matches: 0.8+
   - Recommendations: 0.7-0.8

## 🎉 You're Ready!

The Product Search Agent is now configured and ready to provide intelligent fashion product search capabilities.

**Try it out**: 
```powershell
npm run dev
```

Then chat with the agent to search for products!

---

Need help? Check the full README.md or open an issue on GitHub.
