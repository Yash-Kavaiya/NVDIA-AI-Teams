# NVIDIA Retail AI - Redesigned UI with CopilotKit & Google ADK

## 🎨 Design Overview

This redesign integrates **CopilotKit React components** with **Google ADK (Agent Development Kit)** to create a production-ready, AI-powered retail assistant.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 15)                    │
│                                                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  CopilotKit    │  │  React           │  │  Tailwind   │ │
│  │  Components    │  │  Hooks           │  │  CSS        │ │
│  └────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                              │
│  CopilotSidebar, useCoAgent, useCopilotAction,             │
│  useCopilotReadable, useCopilotChatSuggestions             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ AG-UI Protocol
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Agent Backend (Google ADK + FastAPI)            │
│                                                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  Google ADK    │  │  LlmAgent        │  │  Tools      │ │
│  │  Framework     │  │  (Gemini 2.0)    │  │  (Python)   │ │
│  └────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                              │
│  search_documents_tool, search_images_tool,                 │
│  analyze_inventory_tool, get_state_tool                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Pipelines                           │
│                                                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  Document      │  │  Image           │  │  Inventory  │ │
│  │  Pipeline      │  │  Pipeline        │  │  Data       │ │
│  └────────────────┘  └──────────────────┘  └─────────────┘ │
│                                                              │
│  NVIDIA Embeddings → Qdrant → Reranker → Results           │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### 1. **CopilotKit Integration**
- **`<CopilotSidebar>`** - Pre-built chat UI with NVIDIA branding
- **`useCoAgent`** - Shared state between frontend and Google ADK agent
- **`useCopilotAction`** - Frontend tools with custom rendering
- **`useCopilotReadable`** - Context injection for AI awareness
- **`useCopilotChatSuggestions`** - Dynamic chat suggestions

### 2. **Google ADK Agent**
- **LlmAgent** with Gemini 2.0 Flash Exp model
- **FunctionTool** wrappers for Python tools
- **CallbackContext** for state management
- **Session persistence** with InMemorySessionService

### 3. **Multi-Modal Search**
- **Document Search** - NVIDIA nemoretriever embeddings (2048-dim)
- **Image Search** - Multimodal embeddings for fashion products
- **Inventory Analysis** - AI-powered insights from CSV data

### 4. **Responsive Dashboard**
- Real-time results display
- Tab-based view switching (Documents / Images / Inventory)
- Generative UI with action rendering
- NVIDIA-themed design system

## 📁 File Structure

```
nvdia-ag-ui/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # CopilotKit provider setup
│   │   ├── page.tsx            # Main dashboard with hooks
│   │   └── api/
│   │       └── copilotkit/
│   │           └── route.ts    # Next.js API route
│   └── components/
│       ├── Sidebar.tsx         # Custom sidebar with history
│       ├── ChatInterface.tsx   # (Replaced by CopilotSidebar)
│       └── NvidiaLogo.tsx      # Branding
│
├── agent/
│   ├── retail_agent.py         # NEW: Google ADK agent
│   ├── agent.py                # OLD: Example agent
│   └── requirements.txt        # Python dependencies
│
└── README_REDESIGN.md          # This file
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Frontend
npm install

# Backend (Python agent)
cd agent
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```bash
# Google AI
GOOGLE_API_KEY=your_google_api_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# NVIDIA API
NVIDIA_API_KEY=nvapi-XXXXX

# Qdrant
QDRANT_URL=http://localhost:6333

# Node Environment
NODE_ENV=development
```

### 3. Start Services

```bash
# Terminal 1: Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# Terminal 2: Start Agent Backend
cd agent
python retail_agent.py
# Agent runs on http://localhost:8000

# Terminal 3: Start Next.js Frontend
npm run dev
# Frontend runs on http://localhost:3000
```

## 🛠️ CopilotKit Features Used

### Provider Configuration (`layout.tsx`)

```tsx
<CopilotKit 
  runtimeUrl="/api/copilotkit" 
  agent="retail_ai_agent"
  showDevConsole={true}
>
  {children}
</CopilotKit>
```

### Shared State Management (`page.tsx`)

```tsx
const { state, setState } = useCoAgent<RetailAgentState>({
  name: "retail_ai_agent",
  initialState: {
    documents: [],
    images: [],
    inventory: [],
    queries: [],
    currentAnalysis: null,
  },
});
```

### Context Injection

```tsx
useCopilotReadable({
  description: "Current search results and analysis state",
  value: {
    resultsCount: searchResults.length,
    currentView: selectedView,
    lastQuery: state.queries[state.queries.length - 1],
  },
});
```

### Frontend Actions with Rendering

```tsx
useCopilotAction({
  name: "searchDocuments",
  description: "Search retail compliance documents",
  parameters: [...],
  handler: async ({ query, topK }) => {
    // Call document pipeline
    // Update state
    return { success: true, resultsCount: results.length };
  },
  render: ({ status, result }) => {
    if (status === "executing") {
      return <LoadingIndicator />;
    }
    if (status === "complete") {
      return <SuccessMessage count={result.resultsCount} />;
    }
    return null;
  },
});
```

### Chat Suggestions

```tsx
useCopilotChatSuggestions(
  {
    instructions: "Suggest relevant retail AI actions",
    minSuggestions: 2,
    maxSuggestions: 4,
  },
  [selectedView, state]
);
```

### Pre-built UI

```tsx
<CopilotSidebar
  instructions="You are an AI retail assistant..."
  labels={{
    title: "NVIDIA Retail AI",
    initial: "👋 Welcome! I can help you with...",
  }}
  defaultOpen={true}
>
  {/* Your dashboard content */}
</CopilotSidebar>
```

## 🔧 Google ADK Agent Structure

### Agent Definition (`retail_agent.py`)

```python
root_agent = LlmAgent(
    name="retail_ai_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are the NVIDIA Retail AI Assistant...",
    description="AI assistant for retail operations",
    tools=[
        FunctionTool(search_documents_tool),
        FunctionTool(search_images_tool),
        FunctionTool(analyze_inventory_tool),
        FunctionTool(get_state_tool),
    ],
    callbacks={
        "before_agent": [on_before_agent],
        "before_model": [before_model_modifier],
    }
)
```

### Tool Example

```python
def search_documents_tool(
    tool_context: ToolContext,
    query: str,
    top_k: int = 10
) -> Dict[str, Any]:
    """Search retail compliance documents"""
    # Integration with document_pipeline
    results = ...
    
    # Update agent state
    tool_context.state["documents"] = results
    tool_context.state["queries"].append(query)
    
    return {"status": "success", "results": results}
```

### State Management

```python
def on_before_agent(callback_context: CallbackContext):
    """Initialize state"""
    if "documents" not in callback_context.state:
        callback_context.state["documents"] = []
    # ... initialize other state
    return None
```

## 📊 Data Flow

1. **User Input** → CopilotSidebar chat interface
2. **AG-UI Protocol** → Sends message to Google ADK agent
3. **Agent Processing** → Gemini 2.0 analyzes intent
4. **Tool Invocation** → Calls appropriate Python tool
5. **Pipeline Integration** → Queries NVIDIA embeddings via Qdrant
6. **State Update** → Updates shared state via ToolContext
7. **Response Streaming** → AG-UI streams response back
8. **UI Update** → React components re-render with new data

## 🎨 Design System

### NVIDIA Theme Colors

```css
--nvidia-dark: #1a1a1a
--nvidia-darker: #0f0f0f
--nvidia-green: #76b900
--nvidia-text: #e5e5e5
--nvidia-text-secondary: #a0a0a0
--nvidia-border: #333333
```

### Components

- **CopilotSidebar** - Primary chat interface
- **Dashboard** - Results display grid
- **Tabs** - View switcher (Documents/Images/Inventory)
- **Cards** - Result items with hover effects
- **Loading States** - Animated loading indicators

## 🔗 Integration Points

### Document Pipeline

```python
# TODO: Integrate customer_support/src/retrieval.py
from customer_support.src.retrieval import search_documents

results = search_documents(query, top_k)
```

### Image Pipeline

```python
# TODO: Integrate image_embeddings_pipeline/src/search_engine.py
from image_embeddings_pipeline.src.search_engine import SearchEngine

search_engine = SearchEngine(config)
results = search_engine.search(query, top_k)
```

### Inventory Data

```python
# TODO: Load inventory_data/Warehouse_and_Retail_Sales.csv
import pandas as pd

df = pd.read_csv("inventory_data/Warehouse_and_Retail_Sales.csv")
analysis = analyze_inventory(df, category)
```

## 📈 Next Steps

1. **Connect Document Pipeline** - Integrate `customer_support/src/retrieval.py`
2. **Connect Image Pipeline** - Integrate `image_embeddings_pipeline/src/search_engine.py`
3. **Load Inventory Data** - Read and analyze CSV data
4. **Add Authentication** - Implement user auth with CopilotKit auth config
5. **Deploy to Production** - Containerize and deploy to cloud
6. **Add Analytics** - Track usage metrics and performance
7. **Enhance UI** - Add charts, graphs, and visualizations
8. **Implement Caching** - Cache search results for performance

## 🧪 Testing

```bash
# Test agent endpoint
curl http://localhost:8000/health

# Test document search
curl -X POST http://localhost:8000/api/copilotkit/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Search for safety compliance documents"}'
```

## 📚 Resources

- [CopilotKit Docs](https://docs.copilotkit.ai)
- [Google ADK Docs](https://github.com/google/adk-python)
- [AG-UI Protocol](https://ag-ui.com)
- [NVIDIA AI Models](https://docs.nvidia.com/ai-enterprise)
- [Qdrant Docs](https://qdrant.tech/documentation)

## 🤝 Contributing

See main [README.md](../README.md) for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](../LICENSE)
