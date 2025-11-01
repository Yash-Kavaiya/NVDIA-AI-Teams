# Backend Integration Guide

## Overview
The ChatInterface has been updated to integrate with your ADK middleware backend running at `http://0.0.0.0:8000`.

## Architecture

### Backend (ADK Middleware)
- **URL**: `http://0.0.0.0:8000`
- **Framework**: FastAPI with AG-UI ADK middleware
- **OpenAPI Spec**: Follows CopilotKit ADK standard with `RunAgentInput` schema
- **Agent**: Google ADK agent with Gemini 2.5 Flash model

### Frontend (Next.js + CopilotKit)
- **Route**: `/api/copilotkit/route.ts` - Proxies requests to backend
- **Provider**: `CopilotKit` wraps the app in `layout.tsx`
- **Component**: `ChatInterface.tsx` - Uses CopilotKit hooks

## Key Changes Made

### 1. ChatInterface.tsx Integration

#### Added CopilotKit Hooks
```tsx
import { useCopilotChat, useCopilotReadable } from "@copilotkit/react-core";

const {
  visibleMessages,
  appendMessage,
  isLoading,
} = useCopilotChat();

useCopilotReadable({
  description: "Current chat context and user interaction state",
  value: {
    messageCount: messages.length,
    lastUserMessage: messages.filter(m => m.role === "user").slice(-1)[0]?.content,
  }
});
```

#### Message Synchronization
- CopilotKit messages (`visibleMessages`) are synced with local UI state
- Preserves welcome message on first load
- Maps ADK message format to local Message interface

#### Send Handler
```tsx
const handleSend = async () => {
  if (!input.trim() || isLoading) return;
  
  // Add to local state for immediate UI feedback
  setMessages((prev) => [...prev, userMessage]);
  
  // Send to backend agent
  await appendMessage({
    role: "user",
    content: messageContent,
  } as any);
  
  setInput("");
};
```

#### Loading State
- Replaced `isTyping` state with CopilotKit's `isLoading`
- Shows typing indicator when agent is processing

### 2. Backend Connection

The backend is already configured in `/api/copilotkit/route.ts`:
```typescript
const runtime = new CopilotRuntime({
  agents: {
    "my_agent": new HttpAgent({url: "http://0.0.0.0:8000"}),
  }   
});
```

### 3. Agent State Management

Frontend actions defined in `page.tsx`:
- `searchDocuments` - Query retail compliance PDFs
- `searchImages` - Visual product search
- `analyzeInventory` - Inventory insights

Backend can call these via tool definitions and the agent will execute them.

## Data Flow

1. **User Input** → `ChatInterface.tsx`
2. **appendMessage()** → CopilotKit runtime
3. **HTTP POST** → `/api/copilotkit` (Next.js API route)
4. **Proxy** → `http://0.0.0.0:8000` (FastAPI backend)
5. **ADK Agent** → Processes with Gemini model + tools
6. **Response Stream** ← Backend → CopilotKit → UI
7. **visibleMessages Update** → UI renders assistant message

## Message Schema Mapping

### Frontend (ChatInterface)
```typescript
interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: {
    sources?: string[];
    confidence?: number;
  };
}
```

### Backend (ADK/OpenAPI)
```python
class UserMessage:
    id: str
    role: Literal["user"] = "user"
    content: str
    name: Optional[str] = None

class AssistantMessage:
    id: str
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    name: Optional[str] = None
    toolCalls: Optional[List[ToolCall]] = None
```

## Testing the Integration

### 1. Start Backend
```bash
cd /workspaces/NVDIA-Retail-AI-Teams/nvdia-ag-ui/agent
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
python agent.py
```

Backend should start on `http://0.0.0.0:8000`

### 2. Start Frontend
```bash
cd /workspaces/NVDIA-Retail-AI-Teams/nvdia-ag-ui
npm run dev
```

Frontend starts on `http://localhost:3000`

### 3. Test Flow
1. Open browser to `http://localhost:3000`
2. Type a message in the chat interface
3. Click "Send" or press Enter
4. Watch the message flow through the system
5. See the agent's response appear in the chat

## Debugging

### Check Backend Connection
```bash
curl http://0.0.0.0:8000
# Should return OpenAPI spec JSON
```

### Check CopilotKit Route
```bash
# From browser console or curl
POST http://localhost:3000/api/copilotkit
# Should proxy to backend
```

### Enable Debug Logging
```bash
npm run dev:debug
```

### Check Browser Console
- Network tab: Monitor API calls to `/api/copilotkit`
- Console: Look for CopilotKit debug messages
- React DevTools: Inspect component state

## Extending the Integration

### Add Backend Tools
In `agent/agent.py`:
```python
def search_documents(tool_context: ToolContext, query: str) -> Dict:
    """Search retail compliance documents"""
    # Call your document pipeline
    results = document_pipeline.search(query)
    return {"results": results}

proverbs_agent = LlmAgent(
    tools=[set_proverbs, get_weather, search_documents],  # Add new tool
    ...
)
```

### Add Frontend Actions
In `src/app/page.tsx`:
```typescript
useCopilotAction({
  name: "displayResults",
  description: "Display search results in the UI",
  parameters: [
    {
      name: "results",
      description: "Search results to display",
      required: true,
    },
  ],
  handler({ results }) {
    // Update UI state with results
  },
});
```

## Troubleshooting

### Backend Not Connecting
- Verify backend is running: `ps aux | grep python`
- Check port 8000 is not in use: `lsof -i :8000`
- Ensure `GOOGLE_API_KEY` is set in `.env`

### Messages Not Appearing
- Check browser console for errors
- Verify CopilotKit provider in `layout.tsx`
- Ensure `agent="my_agent"` matches backend agent name

### CORS Issues
- Backend should allow `localhost:3000`
- Check FastAPI CORS middleware configuration

## Next Steps

1. **Integrate NVIDIA Pipelines**: Update backend tools to call your document and image pipelines
2. **Add Metadata**: Pass confidence scores and sources from backend to frontend
3. **Implement Streaming**: Use CopilotKit's streaming for real-time responses
4. **Add Error Handling**: Gracefully handle API failures
5. **Add Authentication**: Secure the agent endpoint if needed

## Resources

- [CopilotKit Docs](https://docs.copilotkit.ai/)
- [AG-UI Client Docs](https://www.npmjs.com/package/@ag-ui/client)
- [Google ADK Docs](https://github.com/google/adk)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
