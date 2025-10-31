# NVIDIA Retail AI Agent Team - UI Components

## 🎨 Component Library

### ChatInterface
The main chat interface with NVIDIA theming.

**Features:**
- Real-time messaging with AI
- Quick suggestion cards
- Message history with timestamps
- Confidence scores and source attribution
- Markdown-like formatting
- Responsive design

**Usage:**
```tsx
import { ChatInterface } from "@/components/ChatInterface";

<ChatInterface />
```

### Sidebar
Navigation sidebar with conversation history.

**Features:**
- New chat button
- Recent conversations list
- User profile section
- Responsive collapse on mobile

**Usage:**
```tsx
import { Sidebar } from "@/components/Sidebar";

<Sidebar onNewChat={() => {/* handle new chat */}} />
```

### NvidiaLogo
NVIDIA branded logo component.

**Props:**
- `className`: Custom CSS classes (default: `"w-32 h-8"`)

**Usage:**
```tsx
import { NvidiaLogo } from "@/components/NvidiaLogo";

<NvidiaLogo className="w-40 h-10 text-white" />
```

### LoadingSpinner
Loading state with NVIDIA branding.

**Usage:**
```tsx
import { LoadingSpinner } from "@/components/LoadingSpinner";

<LoadingSpinner />
```

### EmptyState
Empty state placeholder component.

**Props:**
- `icon`: Emoji or icon string
- `title`: Main heading
- `description`: Supporting text

**Usage:**
```tsx
import { EmptyState } from "@/components/LoadingSpinner";

<EmptyState 
  icon="📄"
  title="No documents found"
  description="Try searching for something else"
/>
```

## 🎨 Color Palette

### CSS Variables
```css
--nvidia-green: #76B900;
--nvidia-green-hover: #5d9200;
--nvidia-dark: #1a1a1a;
--nvidia-darker: #0e0e0e;
--nvidia-text: #e5e5e5;
--nvidia-gray: #8b8b8b;
--nvidia-border: #2a2a2a;
--nvidia-purple: #9b6bff;
--nvidia-red: #ff5757;
```

### Tailwind Classes
```
bg-nvidia-green
text-nvidia-text
border-nvidia-border
hover:bg-nvidia-green-hover
```

## 📐 Layout Patterns

### Full-Height Layout
```tsx
<div className="flex h-screen bg-nvidia-dark">
  <Sidebar />
  <ChatInterface />
</div>
```

### Card Component
```tsx
<div className="bg-nvidia-darker border border-nvidia-border rounded-2xl p-6 shadow-lg">
  {/* Content */}
</div>
```

### Button Styles

**Primary Button:**
```tsx
<button className="bg-nvidia-green hover:bg-nvidia-green-hover text-nvidia-darker font-semibold px-6 py-3 rounded-xl transition-all">
  Click me
</button>
```

**Secondary Button:**
```tsx
<button className="bg-nvidia-darker border border-nvidia-border text-nvidia-text hover:border-nvidia-green px-6 py-3 rounded-xl transition-all">
  Cancel
</button>
```

**Icon Button:**
```tsx
<button className="p-2 rounded-lg bg-nvidia-darker hover:bg-nvidia-dark text-nvidia-text">
  <svg className="w-5 h-5">...</svg>
</button>
```

## 🎯 Input Components

### Text Input
```tsx
<input 
  type="text"
  className="w-full bg-nvidia-dark border border-nvidia-border rounded-xl px-4 py-3 text-nvidia-text focus:border-nvidia-green focus:ring-2 focus:ring-nvidia-green/20"
  placeholder="Enter text..."
/>
```

### Textarea
```tsx
<textarea
  className="w-full bg-nvidia-dark border border-nvidia-border rounded-2xl px-6 py-4 text-nvidia-text resize-none focus:border-nvidia-green focus:ring-2 focus:ring-nvidia-green/20"
  placeholder="Message..."
  rows={3}
/>
```

## 💡 Common Patterns

### Message Bubble
```tsx
<div className="bg-nvidia-darker border border-nvidia-border rounded-2xl px-6 py-4">
  <div className="flex items-start gap-3">
    <div className="w-8 h-8 rounded-full bg-nvidia-green/20 flex items-center justify-center">
      {/* Icon */}
    </div>
    <div className="flex-1">
      <p className="text-nvidia-text">Message content</p>
      <span className="text-nvidia-gray text-xs">12:34 PM</span>
    </div>
  </div>
</div>
```

### Badge/Tag
```tsx
<span className="inline-flex items-center px-3 py-1 rounded-lg bg-nvidia-green/10 text-nvidia-green text-sm">
  AI Generated
</span>
```

### Status Indicator
```tsx
<div className="flex items-center gap-2">
  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-pulse"></div>
  <span className="text-nvidia-gray text-sm">Online</span>
</div>
```

## 🎬 Animations

### Bounce (Loading dots)
```tsx
<div className="flex gap-2">
  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce" />
  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce delay-100" />
  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce delay-200" />
</div>
```

### Spin (Loading spinner)
```tsx
<div className="border-4 border-nvidia-green border-t-transparent rounded-full w-8 h-8 animate-spin" />
```

### Pulse
```tsx
<div className="w-4 h-4 bg-nvidia-green rounded-full animate-pulse" />
```

## 📱 Responsive Utilities

```tsx
{/* Hidden on mobile, visible on desktop */}
<span className="hidden md:block">Desktop only</span>

{/* Different padding on mobile vs desktop */}
<div className="px-4 md:px-6 py-4 md:py-6">
  Content
</div>

{/* Grid layout */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(...)}
</div>
```

## 🔍 Hover Effects

```css
/* Smooth transitions */
.element {
  @apply transition-all duration-200;
}

/* Border glow on hover */
.card {
  @apply hover:border-nvidia-green hover:shadow-lg hover:shadow-nvidia-green/20;
}

/* Text color change */
.link {
  @apply text-nvidia-gray hover:text-nvidia-green;
}
```

## ♿ Accessibility

- Use semantic HTML (`<button>`, `<nav>`, `<main>`)
- Include `aria-label` for icon-only buttons
- Maintain color contrast ratios (WCAG AA)
- Support keyboard navigation
- Add `alt` text for images

Example:
```tsx
<button 
  aria-label="Close dialog"
  className="..."
>
  <svg>...</svg>
</button>
```
