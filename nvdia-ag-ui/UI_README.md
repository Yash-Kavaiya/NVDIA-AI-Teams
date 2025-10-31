# NVIDIA Retail AI Agent Team UI

A modern, ChatGPT-like interface powered by NVIDIA AI technology for retail operations.

## 🎨 Design System

### NVIDIA Brand Colors
- **Primary Green**: `#76B900` - Main accent color for buttons, highlights, and interactive elements
- **Dark Background**: `#1a1a1a` - Main background
- **Darker Background**: `#0e0e0e` - Sidebar and header
- **Text**: `#e5e5e5` - Primary text color
- **Gray**: `#8b8b8b` - Secondary text and icons
- **Border**: `#2a2a2a` - Dividers and borders
- **Purple**: `#9b6bff` - System messages
- **Red**: `#ff5757` - Warnings and delete actions

## 🚀 Features

### Chat Interface
- **Real-time messaging** with AI agent
- **Markdown-like formatting** for rich text responses
- **Message history** with timestamps
- **Confidence scores** and source attribution
- **Quick suggestions** for common tasks
- **Responsive design** for mobile and desktop

### Sidebar Navigation
- **Conversation history** management
- **New chat** creation
- **User profile** display
- **Recent conversations** with timestamps

### AI Capabilities
- 📄 **Document Search** - Query retail compliance PDFs using Docling + NVIDIA embeddings
- 🖼️ **Image Search** - Visual product search with NVIDIA nv-embed-v1
- 📊 **Data Analysis** - Inventory insights with Qdrant vector search
- 💬 **Customer Support** - Knowledge base powered by RAG pipeline

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19
- **AI Integration**: CopilotKit
- **Styling**: Tailwind CSS 4
- **Backend**: Python FastAPI agent
- **Vector DB**: Qdrant
- **Embeddings**: NVIDIA API (llama-3.2-nemoretriever-300m-embed-v2)

## 📦 Installation

```bash
# Install dependencies
npm install

# Setup Python agent
npm run install:agent

# Start development server (runs UI + agent concurrently)
npm run dev
```

## 🎯 Usage

### Starting the Application

```bash
npm run dev
```

This starts:
- **UI**: http://localhost:3000
- **Agent**: Python backend on port 8000
- **CopilotKit**: API route at `/api/copilotkit`

### Environment Variables

Create `.env.local`:

```env
NVIDIA_API_KEY=nvapi-xxxxx
NVIDIA_EMBEDDING_URL=https://integrate.api.nvidia.com/v1
QDRANT_URL=http://localhost:6333
```

### Quick Actions

The chat interface provides quick suggestion buttons:

1. **Search Documents** - Query retail compliance PDFs
2. **Search Products** - Find fashion items by description
3. **Analyze Inventory** - Get stock insights
4. **Customer Support** - Access support docs

## 🎨 Customization

### Updating Colors

Edit `src/app/globals.css`:

```css
:root {
  --nvidia-green: #76B900;
  --nvidia-dark: #1a1a1a;
  /* ... other colors */
}
```

### Adding New Features

1. **Create components** in `src/components/`
2. **Define actions** in `src/app/page.tsx` using `useCopilotAction`
3. **Update agent** in `agent/agent.py` for backend logic

### Styling Guidelines

- Use NVIDIA brand colors from the design system
- Follow the rounded, modern aesthetic (e.g., `rounded-2xl`)
- Maintain accessibility with proper contrast ratios
- Use hover states with `hover:` prefix for interactive elements

## 🔗 Integration

### CopilotKit Actions

```typescript
useCopilotAction({
  name: "searchDocuments",
  description: "Search retail compliance documents",
  parameters: [{ name: "query", required: true }],
  handler({ query }) {
    // Integration logic
  },
});
```

### Backend Agent

The Python agent in `agent/agent.py` handles:
- Document processing with Docling
- Image embedding generation
- Vector search with Qdrant
- Reranking with NVIDIA models

## 📱 Responsive Design

- **Desktop**: Full sidebar + chat interface
- **Tablet**: Collapsible sidebar
- **Mobile**: Optimized single-column layout

## 🐛 Troubleshooting

### Port Conflicts
If port 3000 or 8000 is in use:
```bash
npm run dev:ui -- -p 3001
```

### Python Agent Issues
```bash
cd agent
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Styling Not Applied
Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

## 📄 License

This project uses NVIDIA branding for demonstration purposes. Ensure compliance with NVIDIA brand guidelines for production use.

## 🤝 Contributing

1. Follow SOLID principles for code structure
2. Use TypeScript for type safety
3. Test responsive design on multiple devices
4. Maintain NVIDIA brand consistency

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [CopilotKit Docs](https://docs.copilotkit.ai)
- [NVIDIA AI Foundation](https://www.nvidia.com/en-us/ai-data-science/)
- [Tailwind CSS](https://tailwindcss.com/docs)
