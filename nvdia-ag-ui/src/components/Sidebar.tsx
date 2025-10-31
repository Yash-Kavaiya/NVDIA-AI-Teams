"use client";

import { useState } from "react";

interface SidebarProps {
  onNewChat: () => void;
}

interface Conversation {
  id: string;
  title: string;
  time: string;
}

export function Sidebar({ onNewChat }: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: "1", title: "Product Inventory Query", time: "2 hours ago" },
    { id: "2", title: "Customer Support Analysis", time: "Yesterday" },
    { id: "3", title: "Sales Data Review", time: "2 days ago" },
  ]);

  const handleDeleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((conv) => conv.id !== id));
  };

  return (
    <aside className="w-64 bg-nvidia-darker border-r border-nvidia-border flex flex-col h-screen">
      {/* New Chat Button */}
      <div className="p-4 border-b border-nvidia-border">
        <button
          onClick={onNewChat}
          className="w-full bg-nvidia-green hover:bg-nvidia-green-hover text-nvidia-darker font-semibold px-4 py-3 rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-lg hover:shadow-nvidia-green/20"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2">
        <div className="text-nvidia-gray text-xs font-semibold uppercase tracking-wider px-3 py-2 mb-2">
          Recent Conversations
        </div>
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="relative w-full px-3 py-3 rounded-lg hover:bg-nvidia-dark transition-colors duration-200 group mb-1 cursor-pointer"
            onClick={() => {
              // Handle conversation selection
              console.log("Selected conversation:", conv.id);
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-nvidia-text text-sm font-medium truncate group-hover:text-nvidia-green transition-colors">
                  {conv.title}
                </p>
                <p className="text-nvidia-gray text-xs mt-1">{conv.time}</p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteConversation(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 text-nvidia-gray hover:text-nvidia-red transition-all p-1 rounded hover:bg-nvidia-red/10 flex-shrink-0"
                aria-label="Delete conversation"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-nvidia-border">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-nvidia-dark transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-nvidia-green/20 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-nvidia-green"
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
          <div className="flex-1 min-w-0">
            <p className="text-nvidia-text text-sm font-medium">User Profile</p>
            <p className="text-nvidia-gray text-xs">Retail AI Team</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
