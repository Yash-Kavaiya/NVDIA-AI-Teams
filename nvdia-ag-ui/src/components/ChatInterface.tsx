"use client";

import { useState, useRef, useEffect } from "react";
import { NvidiaLogo } from "./NvidiaLogo";

// Helper function to format timestamp consistently
function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  });
}

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

interface Suggestion {
  icon: string;
  text: string;
  description: string;
}

const quickSuggestions: Suggestion[] = [
  {
    icon: "📄",
    text: "Search Documents",
    description: "Find retail compliance information",
  },
  {
    icon: "🖼️",
    text: "Search Products",
    description: "Visual search for fashion items",
  },
  {
    icon: "📊",
    text: "Analyze Inventory",
    description: "Get insights on stock levels",
  },
  {
    icon: "💬",
    text: "Customer Support",
    description: "Access support documents",
  },
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Initialize messages on client side only to avoid hydration mismatch
  useEffect(() => {
    setIsClient(true);
    setMessages([
      {
        id: "welcome",
        role: "system",
        content: "Welcome to **NVIDIA Retail AI Agent Team**. I can help you with:\n\n• **Document Search** - Query retail compliance PDFs\n• **Image Search** - Find fashion products visually\n• **Data Analysis** - Inventory and sales insights\n• **Customer Support** - Access support knowledge base\n\nWhat would you like to explore today?",
        timestamp: new Date(),
      },
    ]);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response (replace with actual CopilotKit integration)
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm processing your request using **NVIDIA AI embeddings** and our **vector database**. Let me retrieve the most relevant information for you...",
        timestamp: new Date(),
        metadata: {
          confidence: 0.95,
          sources: ["Document Pipeline", "Image Search", "Qdrant DB"],
        },
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: Suggestion) => {
    setInput(suggestion.text);
    textareaRef.current?.focus();
  };

  const formatContent = (content: string) => {
    // Basic markdown-like formatting
    return content
      .split("\n")
      .map((line, i) => {
        // Bold text
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-nvidia-green">$1</strong>');
        // Bullet points
        if (line.trim().startsWith("•")) {
          return `<div key="${i}" class="ml-4 my-1">${line}</div>`;
        }
        return `<div key="${i}" class="my-1">${line || "<br/>"}</div>`;
      })
      .join("");
  };

  // Show minimal loading state during SSR
  if (!isClient) {
    return (
      <div className="flex flex-col h-screen bg-nvidia-dark">
        <header className="bg-nvidia-darker border-b border-nvidia-green/20 px-6 py-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-4">
            <NvidiaLogo className="w-32 h-8 text-white" />
            <div className="h-6 w-px bg-nvidia-green/30" />
            <h1 className="text-white font-semibold text-lg">Retail AI Agent Team</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-nvidia-gray text-sm hidden md:block">Powered by NVIDIA AI</span>
            <div className="w-2 h-2 rounded-full bg-nvidia-green animate-pulse" />
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-nvidia-gray">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-nvidia-dark">
      {/* Header */}
      <header className="bg-nvidia-darker border-b border-nvidia-green/20 px-4 sm:px-6 md:px-8 py-4 md:py-5 flex items-center justify-between shadow-lg flex-shrink-0 relative z-20">
        <div className="flex items-center gap-3 sm:gap-4 min-w-0">
          <NvidiaLogo className="w-28 h-7 sm:w-32 sm:h-8 md:w-36 md:h-9 text-white flex-shrink-0" />
          <div className="h-6 sm:h-7 w-px bg-nvidia-green/30 flex-shrink-0" />
          <h1 className="text-white font-semibold text-base sm:text-lg md:text-xl truncate">Retail AI Agent Team</h1>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <span className="text-nvidia-gray text-sm hidden lg:block">Powered by NVIDIA AI</span>
          <div className="w-2.5 h-2.5 rounded-full bg-nvidia-green animate-pulse" />
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 md:px-8 lg:px-10 py-8 sm:py-10 md:py-12">
        <div className="max-w-5xl mx-auto pb-8">
          {/* Messages */}
          <div className="space-y-5 sm:space-y-6 md:space-y-7">
            {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
          >
            <div
              className={`max-w-full sm:max-w-[90%] md:max-w-4xl w-full ${
                message.role === "user"
                  ? "bg-nvidia-green/10 border border-nvidia-green/30"
                  : message.role === "system"
                  ? "bg-nvidia-purple/5 border border-nvidia-purple/20"
                  : "bg-nvidia-darker border border-nvidia-border"
              } rounded-xl sm:rounded-2xl px-4 sm:px-5 md:px-7 py-4 sm:py-5 md:py-6 shadow-lg`}
            >
              <div className="flex items-start gap-3 sm:gap-4">
                {message.role !== "user" && (
                  <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-nvidia-green/20 flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-5 h-5 sm:w-6 sm:h-6 text-nvidia-green"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div
                    className="text-nvidia-text text-base sm:text-lg leading-relaxed break-words"
                    dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
                  />
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3 mt-3 sm:mt-4">
                    <span className="text-nvidia-gray text-sm">
                      {isClient ? formatTimestamp(message.timestamp) : ''}
                    </span>
                    {message.metadata?.confidence && (
                      <span className="text-nvidia-green text-sm font-medium whitespace-nowrap">
                        {(message.metadata.confidence * 100).toFixed(0)}% confidence
                      </span>
                    )}
                  </div>
                  {message.metadata?.sources && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.metadata.sources.map((source, idx) => (
                        <span
                          key={idx}
                          className="text-xs bg-nvidia-green/10 text-nvidia-green px-3 py-1.5 rounded-lg truncate max-w-[200px] font-medium"
                          title={source}
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-nvidia-green flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-5 h-5 sm:w-6 sm:h-6 text-nvidia-darker"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
          </div>

          {/* Quick Suggestions - Show only on welcome screen */}
          {messages.length === 1 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mt-12 mb-8">
              {quickSuggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="bg-nvidia-darker border border-nvidia-border hover:border-nvidia-green p-6 sm:p-7 rounded-xl text-left transition-all duration-200 hover:shadow-lg hover:shadow-nvidia-green/10 group active:scale-[0.98] min-h-[100px]"
                >
                  <div className="flex items-start gap-3 sm:gap-4">
                    <span className="text-2xl sm:text-3xl flex-shrink-0 leading-none">{suggestion.icon}</span>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-nvidia-text text-base sm:text-lg font-semibold group-hover:text-nvidia-green transition-colors">
                        {suggestion.text}
                      </h3>
                      <p className="text-nvidia-gray text-sm sm:text-base mt-1 line-clamp-2">{suggestion.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start mt-4">
              <div className="max-w-3xl bg-nvidia-darker border border-nvidia-border rounded-2xl px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce delay-100" />
                  <div className="w-2 h-2 rounded-full bg-nvidia-green animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
          {/* Bottom spacer so last items never hide behind the input bar */}
          <div className="h-36 sm:h-40 md:h-44" ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-nvidia-border bg-nvidia-darker px-4 sm:px-6 md:px-8 py-4 sm:py-5 md:py-6 shadow-[0_-4px_20px_rgba(0,0,0,0.5)] flex-shrink-0 relative z-10">
        <div className="max-w-5xl mx-auto">
          <div className="relative flex items-end gap-3 sm:gap-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message NVIDIA Retail AI Agent..."
                className="w-full bg-nvidia-dark border border-nvidia-border rounded-xl sm:rounded-2xl px-4 sm:px-5 md:px-6 py-3 sm:py-3.5 md:py-4 text-base text-nvidia-text placeholder-nvidia-gray focus:outline-none focus:border-nvidia-green focus:ring-2 focus:ring-nvidia-green/20 resize-none min-h-[52px] sm:min-h-[56px] md:min-h-[60px] max-h-[160px] sm:max-h-[180px] md:max-h-[200px] transition-all"
                rows={1}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="bg-nvidia-green hover:bg-nvidia-green-hover disabled:bg-nvidia-gray disabled:cursor-not-allowed disabled:opacity-50 text-nvidia-darker font-semibold px-5 sm:px-6 md:px-8 py-3 sm:py-3.5 md:py-4 rounded-xl sm:rounded-2xl transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-nvidia-green/20 active:scale-95 flex-shrink-0 min-h-[52px] sm:min-h-[56px] md:min-h-[60px]"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
              <span className="hidden sm:inline text-base">Send</span>
            </button>
          </div>
          <p className="text-nvidia-gray text-xs sm:text-sm mt-3 sm:mt-4 text-center px-2">
            NVIDIA AI can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </div>
  );
}
