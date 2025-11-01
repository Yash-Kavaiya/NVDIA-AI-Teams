# Direct API Integration - Final Solution

## Problem Summary

The CopilotKit hooks (`useCopilotChat`, `useCoAgent`) are incompatible with ADK middleware because they internally call methods like `message.isResultMessage()` and `message.isAgentStateMessage()` that don't exist on plain JSON message objects returned by ADK.

## Final Solution: Direct API Communication

We've bypassed CopilotKit's chat hooks entirely and communicate directly with the backend through the CopilotKit API route.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ChatInterface.tsx                       │
│  - Local state management (useState)                         │
│  - Direct fetch() calls                                      │
│  - No useCopilotChat, no useCoAgent                         │
└─────────────────┬───────────────────────────────────────────┘
                  │ fetch('/api/copilotkit')
                  │ with RunAgentInput payload
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              /api/copilotkit/route.ts                        │
│  - CopilotRuntime with HttpAgent                            │
│  - Proxies to backend                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP POST
                  ↓
┌─────────────────────────────────────────────────────────────┐
│              http://0.0.0.0:8000                             │
│  - ADK Middleware (FastAPI)                                  │
│  - Google ADK Agent (Gemini)                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ Streaming response
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      ChatInterface.tsx                       │
│  - Parse Server-Sent Events                                  │
│  - Update UI in real-time                                    │
└─────────────────────────────────────────────────────────────┘
```

## What Changed

### ChatInterface.tsx - Complete Rewrite

#### Old Approach (BROKEN)
```typescript
import { useCopilotChat, useCopilotReadable } from "@copilotkit/react-core";

const { visibleMessages, appendMessage, isLoading } = useCopilotChat();
// ❌ useCopilotChat internally filters messages using methods that don't exist
```

#### New Approach (WORKING)
```typescript
// Simple React state - no CopilotKit hooks
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
const threadIdRef = useRef<string>(`thread-${Date.now()}`);

// Direct API call
const response = await fetch('/api/copilotkit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    threadId: threadIdRef.current,
    runId: `run-${Date.now()}`,
    state: {},
    messages: [{ id, role: "user", content }],
    tools: [],
    context: [],
    forwardedProps: {},
  }),
});
```

### Message Flow

#### 1. User Sends Message
```typescript
const userMessage: Message = {
  id: `user-${Date.now()}`,
  role: "user",
  content: input,
  timestamp: new Date(),
};
setMessages((prev) => [...prev, userMessage]);
```

#### 2. Call Backend API Directly
```typescript
const response = await fetch('http://0.0.0.0:8000', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    threadId: threadIdRef.current,
    runId: `run-${Date.now()}`,
    state: {},
    messages: [{
      id: userMessage.id,
      role: "user",
      content: userMessage.content,
    }],
    tools: [],
    context: [],
    forwardedProps: {},
  }),
});
```
**Important**: We call the backend directly, not through `/api/copilotkit`!

#### 3. Handle ADK Streaming Response
```typescript
const reader = response.body?.getReader();
const decoder = new TextDecoder();
let assistantContent = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value, { stream: true });
  const lines = chunk.split('\n').filter(line => line.trim());

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      // Handle ADK event types
      switch (data.type) {
        case 'TEXT_MESSAGE_START':
          // Create assistant message
          assistantMessageId = data.messageId;
          break;

        case 'TEXT_MESSAGE_CONTENT':
          // Append content delta
          assistantContent += data.delta;
          setMessages((prev) => 
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: assistantContent }
                : msg
            )
          );
          break;

        case 'TEXT_MESSAGE_END':
          // Message complete
          break;
      }
    }
  }
}
```

**ADK Event Types**:
- `RUN_STARTED` - Execution begins
- `TEXT_MESSAGE_START` - Assistant starts responding
- `TEXT_MESSAGE_CONTENT` - Content chunk (delta)
- `TEXT_MESSAGE_END` - Message complete
- `STATE_DELTA` - State update
- `RUN_FINISHED` - Execution complete

## Benefits of This Approach

### ✅ Advantages

1. **No CopilotKit Hook Dependencies**: Avoids the `isResultMessage` error entirely
2. **Full Control**: Complete control over message flow and state
3. **Streaming Support**: Real-time updates as agent responds
4. **Error Handling**: Better error messages and recovery
5. **ADK Compatible**: Works perfectly with ADK middleware
6. **Simple State**: Just React useState, no complex hook interactions
7. **Debuggable**: Easy to see exactly what's being sent/received

### ⚠️ Trade-offs

1. **Manual Implementation**: Have to handle streaming ourselves
2. **No Built-in Features**: Lost some CopilotKit conveniences (auto-retry, etc.)
3. **More Code**: More boilerplate than using hooks

## What Still Uses CopilotKit

### Layout (Provider Only)
```typescript
// layout.tsx
<CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent">
  {children}
</CopilotKit>
```
✅ **Keep this** - It sets up the runtime context

### API Route (Proxy)
```typescript
// /api/copilotkit/route.ts
const runtime = new CopilotRuntime({
  agents: {
    "my_agent": new HttpAgent({url: "http://0.0.0.0:8000"}),
  }   
});
```
✅ **Keep this** - It proxies requests to your backend

### Frontend Actions
```typescript
// page.tsx
useCopilotAction({
  name: "searchDocuments",
  handler: async ({ query }) => {
    // Handle action
  },
});
```
✅ **Keep these** - They still work and let backend call frontend functions

## Testing

### 1. Start Backend
```bash
cd nvdia-ag-ui/agent
python agent.py
# Should show: Running on http://0.0.0.0:8000
```

### 2. Start Frontend
```bash
cd nvdia-ag-ui
npm run dev
# Should show: Ready on http://localhost:3000
```

### 3. Test in Browser
1. Open http://localhost:3000
2. Type a message
3. Click Send
4. Watch browser DevTools Network tab:
   - Should see POST to `/api/copilotkit`
   - Should see streaming response (transfer-encoding: chunked)
5. Agent response should appear in chat

### 4. Debug Issues

#### Check Backend Connection
```bash
curl -X POST http://0.0.0.0:8000 \
  -H "Content-Type: application/json" \
  -d '{
    "threadId": "test",
    "runId": "test",
    "state": {},
    "messages": [{"id": "1", "role": "user", "content": "Hello"}],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

#### Check Frontend Network
- Open browser DevTools → Network tab
- Send a message
- Check the `/api/copilotkit` request:
  - Status: 200 OK
  - Type: text/event-stream or application/json
  - Response should have agent content

#### Common Issues

**Backend not responding**:
- Verify `GOOGLE_API_KEY` is set
- Check backend logs for errors
- Ensure port 8000 is not blocked

**No streaming**:
- Check if backend returns Server-Sent Events format
- Verify response has `Content-Type: text/event-stream`

**CORS errors**:
- Backend should allow `localhost:3000`
- Check FastAPI CORS middleware

## Code Structure

```
nvdia-ag-ui/
├── src/
│   ├── app/
│   │   ├── layout.tsx          ← CopilotKit provider (keep)
│   │   ├── page.tsx            ← useCopilotAction (keep)
│   │   └── api/
│   │       └── copilotkit/
│   │           └── route.ts    ← Proxy to backend (keep)
│   └── components/
│       └── ChatInterface.tsx   ← Direct API calls (NEW)
└── agent/
    └── agent.py                ← ADK middleware backend
```

## Next Steps

### 1. Add Retry Logic
```typescript
const sendMessage = async (retries = 3) => {
  try {
    const response = await fetch('/api/copilotkit', {...});
    return response;
  } catch (error) {
    if (retries > 0) {
      await new Promise(r => setTimeout(r, 1000));
      return sendMessage(retries - 1);
    }
    throw error;
  }
};
```

### 2. Add Message History
```typescript
// Include previous messages for context
body: JSON.stringify({
  messages: [
    ...previousMessages.map(m => ({
      id: m.id,
      role: m.role,
      content: m.content
    })),
    newMessage
  ],
}),
```

### 3. Integrate NVIDIA Pipelines

Update backend `agent.py` to call your existing pipelines:

```python
from customer_support.src.retrieval import search_documents
from image_embeddings_pipeline.src.search_engine import search_images

def search_docs_tool(tool_context: ToolContext, query: str) -> Dict:
    results = search_documents(query, top_k=5)
    return {"results": results}

proverbs_agent = LlmAgent(
    tools=[search_docs_tool, search_images_tool],
    ...
)
```

### 4. Add Source Citations
```typescript
metadata: {
  sources: ["compliance_doc.pdf", "inventory_db"],
  confidence: 0.95,
}
```

## Summary

✅ **Fixed**: Removed all CopilotKit chat hooks  
✅ **Using**: Direct fetch() calls to `/api/copilotkit`  
✅ **Compatible**: Works with ADK middleware  
✅ **Streaming**: Real-time response updates  
✅ **Simple**: Plain React state management  

No more `message.isResultMessage is not a function` errors! 🎉
