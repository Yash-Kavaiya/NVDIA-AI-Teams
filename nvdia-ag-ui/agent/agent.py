"""Shared State feature."""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()
import json
from enum import Enum
from typing import Dict, List, Any, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# ADK imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from google.adk.tools import FunctionTool, ToolContext
from google.genai.types import Content, Part , FunctionDeclaration
from google.adk.models import LlmResponse, LlmRequest
from google.genai import types


from product_search_agent.agent import root_agent as product_search_agent
from review_text_analysis_agent.agent import root_agent as review_text_analysis_agent
from inventory_agent.agent import root_agent as inventory_agent
# from shopping_agent.agent import root_agent as shopping_agent  # Not implemented yet
# from customer_support_agent.agent import root_agent as customer_support_agent  # Requires external customer_support module


from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ProverbsState(BaseModel):
    """List of the proverbs being written."""
    proverbs: list[str] = Field(
        default_factory=list,
        description='The list of already written proverbs',
    )


def on_before_agent(callback_context: CallbackContext):
    """
    Initialize proverbs state if it doesn't exist.
    """

    if "proverbs" not in callback_context.state:
        # Initialize with default recipe
        default_proverbs =     []
        callback_context.state["proverbs"] = default_proverbs


    return None

# --- Define the Callback Function ---
#  modifying the agent's system prompt to incude the current state of the proverbs list
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "retail_coordinator":
        proverbs_json = "No proverbs yet"
        if "proverbs" in callback_context.state and callback_context.state["proverbs"] is not None:
            try:
                proverbs_json = json.dumps(callback_context.state["proverbs"], indent=2)
            except Exception as e:
                proverbs_json = f"Error serializing proverbs: {str(e)}"
        # --- Modification Example ---
        # Add a prefix to the system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
        prefix = f"""You are a helpful assistant for maintaining a list of proverbs.
        This is the current state of the list of proverbs: {proverbs_json}
        When you modify the list of proverbs (wether to add, remove, or modify one or more proverbs), use the set_proverbs tool to update the list."""
        # Ensure system_instruction is Content and parts list exists
        if not isinstance(original_instruction, types.Content):
            # Handle case where it might be a string (though config expects Content)
            original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
        if not original_instruction.parts:
            original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist

        # Modify the text of the first part
        modified_text = prefix + (original_instruction.parts[0].text or "")
        original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

    return None

# --- Define the Callback Function ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Stop the consecutive tool calling of the agent"""
    agent_name = callback_context.agent_name
    # --- Inspection ---
    if agent_name == "retail_coordinator":
        original_text = ""
        if llm_response.content and llm_response.content.parts:
            # Assuming simple text response for this example
            if  llm_response.content.role=='model' and llm_response.content.parts[0].text:
                original_text = llm_response.content.parts[0].text
                callback_context._invocation_context.end_invocation = True

        elif llm_response.error_message:
            return None
        else:
            return None # Nothing to modify
    return None
from google.adk.models.lite_llm import LiteLlm
retail_coordinator = LlmAgent(
        name="retail_coordinator",
        model=LiteLlm(model="nvidia_nim/nvidia/llama-3.1-nemotron-nano-8b-v1"),
        instruction=f"""
        You are the main coordinator for a comprehensive retail agent team. Your role is to:
    
    1. Intelligent Request Routing:
       - Analyze customer requests and identify the appropriate specialized agent(s)
       - Route simple queries to a single agent
       - Coordinate multiple agents for complex, multi-faceted requests
       - Ensure the right specialist handles each aspect of the request
    
    2. Multi-Agent Coordination:
       - Orchestrate parallel processing when multiple agents are needed
       - Manage sequential workflows (e.g., search → inventory → cart)
       - Synthesize responses from multiple agents into coherent answers
       - Handle dependencies between agent tasks
    
    3. Context Management:
       - Maintain conversation context across agent handoffs
       - Remember customer preferences and previous interactions
       - Track the state of ongoing tasks and processes
       - Ensure continuity in multi-turn conversations
    
    4. Response Synthesis:
       - Combine outputs from multiple agents intelligently
       - Present unified, coherent responses to customers
       - Eliminate redundancy in multi-agent responses
       - Prioritize and organize information effectively
    
    5. Escalation and Fallback:
       - Handle edge cases that don't fit a specific agent
       - Provide graceful fallbacks when agents can't fulfill requests
       - Escalate to human support when necessary
       - Guide customers through complex scenarios
    
    Available Specialized Sub-Agents:
    
    🔍 product_search_agent
       - Product searches and filtering
       - Product comparisons and recommendations
       - Detailed product information
       - Alternative suggestions
    
    📊 review_text_analysis_agent
       - Customer review analysis
       - Sentiment analysis
       - Product feedback insights
       - Review summarization
    
    📦 inventory_agent
       - Stock availability checks
       - Multi-location inventory tracking
       - Delivery time estimates
       - Restock notifications
    
    🛒 shopping_agent
       - Shopping cart management
       - Checkout processing
       - Discount and coupon application
       - Order placement
    
    💬 customer_support_agent
       - Order inquiries and tracking
       - Returns, refunds, and exchanges
       - Policy information
       - Issue resolution
    
    Coordination Strategies:
    
    - For product browsing: product_search_agent → inventory_agent
    - For informed purchases: product_search_agent → review_text_analysis_agent → inventory_agent
    - For cart operations: shopping_agent (may consult inventory_agent)
    - For post-purchase: customer_support_agent
    - For complex queries: Coordinate multiple agents as needed
    
    Always prioritize customer satisfaction, provide clear and helpful responses, 
    and ensure a seamless experience across all retail operations.
        """,
        sub_agents=[product_search_agent,review_text_analysis_agent,inventory_agent],
        # customer_support_agent temporarily disabled due to external dependencies
        before_agent_callback=on_before_agent,
        before_model_callback=before_model_modifier,
        after_model_callback = simple_after_model_modifier
    )

# Create ADK middleware agent instance
adk_retail_coordinator = ADKAgent(
    adk_agent=retail_coordinator,
    app_name="retail_coordinator_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Proverbs Agent")

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health check endpoint for Kubernetes
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    return {
        "status": "healthy",
        "service": "nvidia-retail-ai-agent-backend",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_retail_coordinator, path="/")

if __name__ == "__main__":
    import os
    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
