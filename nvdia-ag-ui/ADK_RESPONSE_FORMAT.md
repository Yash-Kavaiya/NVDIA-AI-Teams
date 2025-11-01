# ADK Backend Response Format

## Overview

The ADK middleware backend (`http://0.0.0.0:8000`) returns Server-Sent Events (SSE) with different event types during agent execution.

## Request Format

```typescript
POST http://0.0.0.0:8000
Content-Type: application/json

{
  "threadId": "thread-12345",      // Unique thread identifier
  "runId": "run-67890",            // Unique run identifier
  "state": {},                     // Agent state (optional)
  "messages": [                    // Conversation messages
    {
      "id": "msg-1",
      "role": "user",              // "user" | "assistant" | "system"
      "content": "Hello"
    }
  ],
  "tools": [],                     // Available tools (optional)
  "context": [],                   // Additional context (optional)
  "forwardedProps": {}             // Custom properties (optional)
}
```

## Response Format

### Server-Sent Events (SSE)

The response is a stream of events in SSE format:

```
data: {"type":"RUN_STARTED","threadId":"thread-12345","runId":"run-67890"}

data: {"type":"TEXT_MESSAGE_START","messageId":"msg-abc","role":"assistant"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":"Hello"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":" there!"}

data: {"type":"TEXT_MESSAGE_END","messageId":"msg-abc"}

data: {"type":"RUN_FINISHED","threadId":"thread-12345","runId":"run-67890"}
```

## Event Types

### 1. RUN_STARTED
Indicates the agent execution has begun.

```json
{
  "type": "RUN_STARTED",
  "threadId": "thread-12345",
  "runId": "run-67890"
}
```

### 2. STATE_DELTA
Represents a change in the agent's state.

```json
{
  "type": "STATE_DELTA",
  "delta": [
    {
      "op": "add",              // "add" | "remove" | "replace"
      "path": "/proverbs",      // JSON Pointer path
      "value": []               // New value
    }
  ]
}
```

### 3. TEXT_MESSAGE_START
Marks the beginning of an assistant message.

```json
{
  "type": "TEXT_MESSAGE_START",
  "messageId": "c49fce24-9f5c-4d4e-a413-d0f595f59832",
  "role": "assistant"
}
```

**Action**: Create a new message object in the UI with this messageId.

### 4. TEXT_MESSAGE_CONTENT
Contains a chunk (delta) of the message content.

```json
{
  "type": "TEXT_MESSAGE_CONTENT",
  "messageId": "c49fce24-9f5c-4d4e-a413-d0f595f59832",
  "delta": "Hello! How can I help you?"
}
```

**Action**: Append `delta` to the message with matching `messageId`.

**Note**: You'll receive multiple `TEXT_MESSAGE_CONTENT` events as the model generates text. Concatenate all deltas to build the complete message.

### 5. TEXT_MESSAGE_END
Marks the completion of a message.

```json
{
  "type": "TEXT_MESSAGE_END",
  "messageId": "c49fce24-9f5c-4d4e-a413-d0f595f59832"
}
```

**Action**: Finalize the message (no more content will be added).

### 6. STATE_SNAPSHOT
Provides a complete snapshot of the current state.

```json
{
  "type": "STATE_SNAPSHOT",
  "snapshot": {
    "context": {
      "conversation": [],
      "user": {
        "name": "",
        "timezone": "UTC"
      },
      "app": {
        "version": "unknown"
      }
    },
    "state": {}
  }
}
```

### 7. RUN_FINISHED
Indicates the agent execution has completed.

```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-12345",
  "runId": "run-67890"
}
```

## Frontend Implementation

### Parsing SSE Stream

```typescript
const response = await fetch('http://0.0.0.0:8000', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({...})
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();
let assistantContent = "";
let assistantMessageId = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value, { stream: true });
  const lines = chunk.split('\n').filter(line => line.trim());

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      try {
        const event = JSON.parse(line.slice(6));
        handleEvent(event);
      } catch (e) {
        console.error('Parse error:', e);
      }
    }
  }
}
```

### Event Handler

```typescript
function handleEvent(event: any) {
  switch (event.type) {
    case 'RUN_STARTED':
      console.log('Agent started:', event.runId);
      break;

    case 'TEXT_MESSAGE_START':
      // Create new message
      assistantMessageId = event.messageId;
      setMessages(prev => [...prev, {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }]);
      break;

    case 'TEXT_MESSAGE_CONTENT':
      // Append content
      assistantContent += event.delta;
      setMessages(prev => 
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: assistantContent }
            : msg
        )
      );
      break;

    case 'TEXT_MESSAGE_END':
      console.log('Message complete');
      break;

    case 'RUN_FINISHED':
      console.log('Agent finished');
      break;
  }
}
```

## Example Complete Flow

### Request
```bash
curl -X POST http://0.0.0.0:8000 \
  -H "Content-Type: application/json" \
  -d '{
    "threadId": "test-123",
    "runId": "run-456",
    "state": {},
    "messages": [{"id": "1", "role": "user", "content": "Hello"}],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

### Response Stream
```
data: {"type":"RUN_STARTED","threadId":"test-123","runId":"run-456"}

data: {"type":"STATE_DELTA","delta":[{"op":"add","path":"/proverbs","value":[]}]}

data: {"type":"TEXT_MESSAGE_START","messageId":"msg-abc","role":"assistant"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":"Hello"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":"!"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":" How"}

data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg-abc","delta":" can I help you?"}

data: {"type":"TEXT_MESSAGE_END","messageId":"msg-abc"}

data: {"type":"STATE_SNAPSHOT","snapshot":{...}}

data: {"type":"RUN_FINISHED","threadId":"test-123","runId":"run-456"}
```

### Final Result
**User**: Hello  
**Assistant**: Hello! How can I help you?

## Error Handling

### HTTP Errors
```typescript
if (!response.ok) {
  throw new Error(`HTTP error! status: ${response.status}`);
}
```

### Parse Errors
```typescript
try {
  const event = JSON.parse(line.slice(6));
  handleEvent(event);
} catch (e) {
  console.error('Failed to parse event:', line, e);
}
```

### Timeout
```typescript
const timeoutId = setTimeout(() => {
  reader.cancel();
  throw new Error('Response timeout');
}, 30000); // 30 second timeout
```

## Testing

### Test Backend Directly
```bash
curl -N -X POST http://0.0.0.0:8000 \
  -H "Content-Type: application/json" \
  -d '{
    "threadId": "test",
    "runId": "test",
    "state": {},
    "messages": [{"id": "1", "role": "user", "content": "Tell me a proverb"}],
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

The `-N` flag disables curl's buffering so you see events as they arrive.

## Common Issues

### 400 Bad Request
- Check that all required fields are present in the request
- Verify `messages` array has proper structure
- Ensure `role` is one of: "user", "assistant", "system", "developer", "tool"

### 422 Validation Error
- Check the OpenAPI schema requirements
- All `additionalProperties: false` schemas are strict
- UserMessage requires `id` and `content`

### Connection Timeout
- Verify backend is running: `ps aux | grep python`
- Check port 8000: `lsof -i :8000`
- Test with curl first

### CORS Issues
If calling from browser, backend needs CORS headers:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

## Summary

- **Format**: Server-Sent Events (SSE)
- **Content-Type**: `text/event-stream`
- **Line Format**: `data: <JSON>\n\n`
- **Key Events**: `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TEXT_MESSAGE_END`
- **Streaming**: Yes - multiple `TEXT_MESSAGE_CONTENT` events
- **State Management**: `STATE_DELTA` and `STATE_SNAPSHOT` events
