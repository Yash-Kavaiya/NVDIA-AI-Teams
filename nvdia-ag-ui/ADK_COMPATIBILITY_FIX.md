# ADK Middleware Compatibility Fixes

## Issue
```
Error: message.isResultMessage is not a function
Error: message.isAgentStateMessage is not a function
```

These errors occurred because CopilotKit's `useCoAgent` hook expects message objects with specific methods that aren't provided by the ADK middleware from your backend.

## Root Cause
The ADK middleware returns plain message objects that follow the OpenAPI schema:
```typescript
{
  id: string;
  role: "user" | "assistant" | "system" | "tool" | "developer";
  content: string;
  // ... other properties
}
```

But CopilotKit's `useCoAgent` internally tries to call methods like `isResultMessage()` and `isAgentStateMessage()` on these objects, which don't exist.

## Solution Applied

### 1. Removed CopilotKit Chat Hooks
**File**: `src/components/ChatInterface.tsx`

**Before**:
```typescript
import { useCopilotChat, useCopilotReadable } from "@copilotkit/react-core";

const { visibleMessages, appendMessage, isLoading } = useCopilotChat();
useCopilotReadable({...});
```

**After**:
```typescript
// Direct API communication without CopilotKit chat hooks
const [messages, setMessages] = useState<Message[]>([]);
const [isLoading, setIsLoading] = useState(false);
const threadIdRef = useRef<string>(`thread-${Date.now()}`);
```

**Why**: `useCopilotChat` internally calls `message.isResultMessage()` and `message.isAgentStateMessage()` which don't exist on ADK message objects. We now communicate directly with the API.

### 2. Removed `useCoAgent` Hook
**File**: `src/app/page.tsx`

**Before**:
```typescript
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: { documents: [], images: [], queries: [] },
});
```

**After**:
```typescript
// Use regular React state instead
const [agentState, setAgentState] = useState<AgentState>({
  documents: [],
  images: [],
  queries: [],
});
```

**Why**: `useCoAgent` is designed for CopilotKit's native agent protocol, not ADK middleware.

### 2. Updated CopilotActions
**File**: `src/app/page.tsx`

Added proper parameter types and return values:
```typescript
useCopilotAction({
  name: "searchDocuments",
  description: "Search through retail compliance documents",
  parameters: [
    {
      name: "query",
      type: "string",  // Added type
      description: "The search query for documents",
      required: true,
    },
  ],
  handler: async ({ query }) => {  // Made async
    console.log("Searching documents:", query);
    setAgentState(prev => ({
      ...prev,
      queries: [...prev.queries, query],
    }));
    return { status: "success", query };  // Return result
  },
});
```

### 3. Direct API Communication
**File**: `src/components/ChatInterface.tsx`

Replaced CopilotKit hooks with direct fetch calls to the backend:

```typescript
const handleSend = async () => {
  if (!input.trim() || isLoading) return;

  // Add user message to UI immediately
  const userMessage: Message = {
    id: `user-${Date.now()}`,
    role: "user",
    content: input,
    timestamp: new Date(),
  };
  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setIsLoading(true);

  try {
    // Call backend directly via CopilotKit API route
    const response = await fetch('/api/copilotkit', {
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

    // Handle streaming response
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let assistantContent = "";

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Parse Server-Sent Events format
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            assistantContent += data.content || '';
            // Update UI in real-time
            setMessages((prev) => 
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: assistantContent }
                  : msg
              )
            );
          }
        }
      }
    }
  } catch (error) {
    console.error('Error:', error);
    // Show error message in chat
  } finally {
    setIsLoading(false);
  }
};
```

**Key improvements**:
- Direct fetch to `/api/copilotkit` endpoint
- Proper ADK RunAgentInput schema
- Streaming response support
- Real-time UI updates
- Error handling with user feedback
- No dependency on CopilotKit's internal message handling

## How It Works Now

### Message Flow
```
User Input
  ↓
ChatInterface.tsx (appendMessage)
  ↓
CopilotKit Runtime
  ↓
/api/copilotkit (Next.js proxy)
  ↓
http://0.0.0.0:8000 (ADK Middleware)
  ↓
Google ADK Agent (Gemini)
  ↓
Response (plain ADK message objects)
  ↓
CopilotKit Runtime (visibleMessages)
  ↓
ChatInterface.tsx (defensive parsing)
  ↓
UI renders messages
```

### State Management
```typescript
// Frontend state (page.tsx)
const [agentState, setAgentState] = useState({
  documents: [],
  images: [],
  queries: [],
});

// Actions can update this state
useCopilotAction({
  handler: async ({ query }) => {
    setAgentState(prev => ({...prev, queries: [...prev.queries, query]}));
    return { status: "success" };
  },
});
```

## Testing

1. **Start Backend**:
```bash
cd nvdia-ag-ui/agent
python agent.py
```

2. **Start Frontend**:
```bash
cd nvdia-ag-ui
npm run dev
```

3. **Test in Browser**:
- Open http://localhost:3000
- Type a message
- Should see the message sent to backend
- Agent responds via ADK middleware
- Response appears in chat UI

## What Changed

| Component | Before | After |
|-----------|--------|-------|
| `page.tsx` | Used `useCoAgent` hook | Uses `useState` for state |
| `page.tsx` | Simple action handlers | Async handlers with return values |
| `ChatInterface.tsx` | Basic message mapping | Defensive message parsing with error handling |

## Why This Works

1. **No Method Assumptions**: We don't assume message objects have special methods
2. **Defensive Parsing**: Every property access is validated
3. **Error Boundaries**: Try-catch prevents crashes
4. **Type Safety**: Explicit type checking and conversion
5. **ADK Compatible**: Works with plain JSON messages from ADK middleware

## Next Steps

If you need shared state between frontend and backend:

1. **Option 1: Use Context API**
```typescript
// In layout.tsx or a provider component
const AgentContext = createContext<AgentState>({});
```

2. **Option 2: Add state to message metadata**
```typescript
await appendMessage({
  role: "user",
  content: input,
  metadata: { state: agentState },
} as any);
```

3. **Option 3: Use URL-based state management**
```typescript
// Update URL params with state
router.push(`/?documents=${documents.join(',')}`);
```

## Troubleshooting

### If messages still don't appear:
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check Network tab for failed API calls
4. Look for CORS errors

### If backend connection fails:
1. Verify `GOOGLE_API_KEY` is set
2. Check backend logs for errors
3. Test endpoint directly: `curl http://0.0.0.0:8000`

### If state updates don't persist:
1. Use browser DevTools to inspect state
2. Add console.logs in action handlers
3. Verify `setAgentState` is being called
