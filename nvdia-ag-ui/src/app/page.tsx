"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
import { Sidebar } from "@/components/Sidebar";

export default function CopilotKitPage() {
  const [showSidebar, setShowSidebar] = useState(true);
  
  // Local state management (not using useCoAgent due to ADK middleware compatibility)
  const [agentState, setAgentState] = useState<AgentState>({
    documents: [],
    images: [],
    queries: [],
  });

  // 🪁 Frontend Actions for Retail AI
  useCopilotAction({
    name: "searchDocuments",
    description: "Search through retail compliance documents",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "The search query for documents",
        required: true,
      },
    ],
    handler: async ({ query }) => {
      console.log("Searching documents:", query);
      setAgentState(prev => ({
        ...prev,
        queries: [...prev.queries, query],
      }));
      // Integration with document pipeline will go here
      return { status: "success", query };
    },
  });

  useCopilotAction({
    name: "searchImages",
    description: "Search through fashion product images",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "The search query for images",
        required: true,
      },
    ],
    handler: async ({ query }) => {
      console.log("Searching images:", query);
      setAgentState(prev => ({
        ...prev,
        queries: [...prev.queries, query],
      }));
      // Integration with image pipeline will go here
      return { status: "success", query };
    },
  });

  useCopilotAction({
    name: "analyzeInventory",
    description: "Analyze retail inventory and provide insights",
    parameters: [
      {
        name: "category",
        type: "string",
        description: "Product category to analyze",
        required: true,
      },
    ],
    handler: async ({ category }) => {
      console.log("Analyzing inventory:", category);
      setAgentState(prev => ({
        ...prev,
        queries: [...prev.queries, `inventory:${category}`],
      }));
      // Integration with retrieval pipeline will go here
      return { status: "success", category };
    },
  });

  const handleNewChat = () => {
    // Reset chat state
    setAgentState({
      documents: [],
      images: [],
      queries: [],
    });
  };

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-nvidia-dark">
      {/* Sidebar */}
      {showSidebar && <Sidebar onNewChat={handleNewChat} />}

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        {/* Toggle Sidebar Button - Only show when sidebar is hidden */}
        {!showSidebar && (
          <button
            onClick={() => setShowSidebar(true)}
            className="absolute top-3 left-3 sm:top-4 sm:left-4 md:top-6 md:left-6 z-20 bg-nvidia-darker hover:bg-nvidia-dark border border-nvidia-border text-nvidia-text p-2 sm:p-2.5 rounded-lg transition-all duration-200 shadow-lg hover:border-nvidia-green active:scale-95"
            aria-label="Open sidebar"
          >
            <svg
              className="w-4 h-4 sm:w-5 sm:h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        )}

        <ChatInterface />
      </div>
    </main>
  );
}

// State of the agent for Retail AI
type AgentState = {
  documents: any[];
  images: any[];
  queries: string[];
}