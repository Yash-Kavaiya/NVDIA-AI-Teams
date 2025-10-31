"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
import { Sidebar } from "@/components/Sidebar";

export default function CopilotKitPage() {
  const [showSidebar, setShowSidebar] = useState(true);

  // 🪁 Shared State: https://docs.copilotkit.ai/coagents/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      documents: [],
      images: [],
      queries: [],
    },
  });

  // 🪁 Frontend Actions for Retail AI
  useCopilotAction({
    name: "searchDocuments",
    description: "Search through retail compliance documents",
    parameters: [
      {
        name: "query",
        description: "The search query for documents",
        required: true,
      },
    ],
    handler({ query }) {
      console.log("Searching documents:", query);
      // Integration with document pipeline will go here
    },
  });

  useCopilotAction({
    name: "searchImages",
    description: "Search through fashion product images",
    parameters: [
      {
        name: "query",
        description: "The search query for images",
        required: true,
      },
    ],
    handler({ query }) {
      console.log("Searching images:", query);
      // Integration with image pipeline will go here
    },
  });

  useCopilotAction({
    name: "analyzeInventory",
    description: "Analyze retail inventory and provide insights",
    parameters: [
      {
        name: "category",
        description: "Product category to analyze",
        required: true,
      },
    ],
    handler({ category }) {
      console.log("Analyzing inventory:", category);
      // Integration with retrieval pipeline will go here
    },
  });

  const handleNewChat = () => {
    // Reset chat state
    setState({
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
