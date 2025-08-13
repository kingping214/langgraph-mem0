import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from anthropic import Anthropic
from mem0 import Memory
import json

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    memory_retrieved: Optional[Dict[str, Any]]

class MemoryAgent:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Configure mem0 to use Ollama for embeddings and Anthropic for LLM
        self.memory = Memory.from_config({
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text:latest",
                    "ollama_base_url": "http://localhost:11434",
                    "embedding_dims": 768
                }
            },
            "llm": {
                "provider": "anthropic",
                "config": {
                    "model": "claude-sonnet-4-0",
                    "api_key": os.getenv("ANTHROPIC_API_KEY")
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test",
                    "path": "db"
                }
            }
        })
        
    def retrieve_memory(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve relevant memories for the current conversation"""
        user_id = state["user_id"]
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Search for relevant memories
        try:
            memories_result = self.memory.search(query=last_message, user_id=user_id)
            memories = memories_result.get('results', []) if isinstance(memories_result, dict) else memories_result
        except Exception as e:
            memories = []
        
        return {
            "memory_retrieved": {
                "memories": memories,
                "count": len(memories)
            }
        }
    
    def generate_response(self, state: AgentState) -> Dict[str, Any]:
        """Generate response using Anthropic API with memory context"""
        user_id = state["user_id"]
        messages = state["messages"]
        memories = state.get("memory_retrieved", {}).get("memories", [])
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant memories from previous conversations:\n"
            for mem in memories[:3]:  # Use top 3 most relevant memories
                memory_context += f"- {mem.get('memory', '')}\n"
        
        # Get the last user message
        last_message = messages[-1].content if messages else ""
        
        # Create prompt with memory context
        system_prompt = f"""You are a helpful AI assistant with access to conversation history and memories. 
        Use the provided memories to give more personalized and contextual responses.{memory_context}
        
        Remember to be conversational and reference past interactions when relevant."""
        
        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-0",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": last_message}]
            )
            
            assistant_message = response.content[0].text
            
            # Store the conversation in memory
            self.memory.add(
                messages=[
                    {"role": "user", "content": last_message},
                    {"role": "assistant", "content": assistant_message}
                ],
                user_id=user_id
            )
            
            return {
                "messages": [{"role": "assistant", "content": assistant_message}]
            }
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            return {
                "messages": [{"role": "assistant", "content": error_message}]
            }
    
    def create_graph(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve_memory", self.retrieve_memory)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define the flow
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()

def main():
    """Main function to demonstrate the memory agent"""
    agent = MemoryAgent()
    graph = agent.create_graph()
    
    print("Memory-enabled AI Agent Demo")
    print("Type 'quit' to exit\n")
    
    user_id = "demo_user"
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'quit':
            break
            
        # Run the graph
        result = graph.invoke({
            "messages": [{"role": "user", "content": user_input}],
            "user_id": user_id
        })
        
        # Print the response
        if result["messages"]:
            print(f"Assistant: {result['messages'][-1]['content']}\n")

if __name__ == "__main__":
    main()
