import os
import re
import html
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from anthropic import Anthropic
from mem0 import Memory

load_dotenv()

# Configure logging for security monitoring
# Get log level from environment, default to WARNING for console
console_log_level = getattr(logging, os.getenv('LOG_LEVEL', 'WARNING').upper(), logging.WARNING)

# Configure file handler for comprehensive logging
file_handler = logging.FileHandler('security.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure console handler for minimal output
console_handler = logging.StreamHandler()
console_handler.setLevel(console_log_level)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Set root logger to INFO for file logging, but control console output
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# Suppress third-party library logging in console
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('anthropic').setLevel(logging.WARNING)
logging.getLogger('ollama').setLevel(logging.WARNING)
logging.getLogger('chromadb').setLevel(logging.WARNING)
logging.getLogger('mem0').setLevel(logging.WARNING)

security_logger = logging.getLogger('security')

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    memory_retrieved: Optional[Dict[str, Any]]

class MemoryAgent:
    def __init__(self):
        # Validate required environment variables
        self._validate_environment()
        
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.max_input_length = 10000  # Maximum input length
        self.max_memory_length = 5000  # Maximum memory content length
        
        # Configure mem0 to use Ollama for embeddings and Anthropic for LLM
        self.memory = Memory.from_config({
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": os.getenv("OLLAMA_MODEL"),
                    "ollama_base_url": os.getenv("OLLAMA_BASE_URL"),
                    "embedding_dims": int(os.getenv("OLLAMA_EMBEDDING_DIMS"))
                }
            },
            "llm": {
                "provider": "anthropic",
                "config": {
                    "model": os.getenv("ANTHROPIC_MODEL"),
                    "api_key": os.getenv("ANTHROPIC_API_KEY")
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": os.getenv("CHROMA_COLLECTION_NAME"),
                    "path": os.getenv("CHROMA_DB_PATH")
                }
            }
        })
    
    def _validate_environment(self) -> None:
        """Validate all required environment variables are set"""
        required_vars = [
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_MODEL", 
            "OLLAMA_MODEL",
            "OLLAMA_BASE_URL",
            "OLLAMA_EMBEDDING_DIMS",
            "CHROMA_COLLECTION_NAME",
            "CHROMA_DB_PATH"
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_vars.append(var)
        
        if missing_vars:
            security_logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate specific formats
        try:
            int(os.getenv("OLLAMA_EMBEDDING_DIMS"))
        except (ValueError, TypeError):
            raise ValueError("OLLAMA_EMBEDDING_DIMS must be a valid integer")
        
        # Validate URL format
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        if not re.match(r'^https?://[\w\.-]+(:\d+)?/?$', ollama_url):
            raise ValueError("OLLAMA_BASE_URL must be a valid HTTP/HTTPS URL")
        
        security_logger.info("Environment validation completed successfully")
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Check length limits
        if len(text) > self.max_input_length:
            security_logger.warning(f"Input length exceeded: {len(text)} > {self.max_input_length}")
            raise ValueError(f"Input too long. Maximum length is {self.max_input_length} characters")
        
        # Remove potential script injections and control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        sanitized = html.escape(sanitized, quote=True)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>[\s\S]*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Log only if dangerous patterns were actually detected (not just HTML escaping)
        original_after_cleanup = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        html_escaped = html.escape(original_after_cleanup, quote=True)
        if sanitized != html_escaped:
            security_logger.warning("Input sanitization applied - potentially malicious content detected")
        
        return sanitized.strip()
    
    def _validate_memory_content(self, content: str) -> str:
        """Validate and sanitize memory content before storage"""
        if not isinstance(content, str):
            raise ValueError("Memory content must be a string")
        
        if len(content) > self.max_memory_length:
            security_logger.warning(f"Memory content length exceeded: {len(content)} > {self.max_memory_length}")
            content = content[:self.max_memory_length] + "...[truncated]"
        
        # Apply same sanitization as input
        return self._sanitize_input(content)
    
    def retrieve_memory(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve relevant memories for the current conversation"""
        user_id = state["user_id"]
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Validate and sanitize the search query
        try:
            sanitized_query = self._sanitize_input(last_message)
        except ValueError as e:
            security_logger.error(f"Invalid search query from user {user_id}: {str(e)}")
            return {"memory_retrieved": {"memories": [], "count": 0}}
        
        # Search for relevant memories
        try:
            memories_result = self.memory.search(query=sanitized_query, user_id=user_id)
            memories = memories_result.get('results', []) if isinstance(memories_result, dict) else memories_result
            
            # Validate retrieved memories
            validated_memories = []
            for memory in memories:
                if isinstance(memory, dict) and 'memory' in memory:
                    try:
                        validated_content = self._validate_memory_content(memory['memory'])
                        validated_memory = memory.copy()
                        validated_memory['memory'] = validated_content
                        validated_memories.append(validated_memory)
                    except ValueError:
                        security_logger.warning(f"Invalid memory content detected for user {user_id}")
                        continue
            
            memories = validated_memories
            
        except Exception as e:
            security_logger.error(f"Memory retrieval error for user {user_id}: {str(e)}")
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
        memory_data = state.get("memory_retrieved", {})
        memories = memory_data.get("memories", [])
        
        # Build context from memories
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant memories from previous conversations:\n"
            for mem in memories[:3]:  # Use top 3 most relevant memories
                memory_context += f"- {mem.get('memory', '')}\n"
        
        # Get and sanitize the last user message
        last_message = messages[-1].content if messages else ""
        try:
            last_message = self._sanitize_input(last_message)
        except ValueError as e:
            security_logger.error(f"Invalid message content from user {user_id}: {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": "I'm sorry, but your message contains invalid content. Please try again with a different message."}]
            }
        
        # Create prompt with memory context
        system_prompt = f"""You are a helpful AI assistant with access to conversation history and memories. 
        Use the provided memories to give more personalized and contextual responses.{memory_context}
        
        Remember to be conversational and reference past interactions when relevant."""
        
        try:
            response = self.anthropic.messages.create(
                model=os.getenv("ANTHROPIC_MODEL"),
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": last_message}]
            )
            
            assistant_message = response.content[0].text
            
            # Validate and sanitize assistant response before storing
            try:
                sanitized_response = self._validate_memory_content(assistant_message)
                sanitized_user_message = self._validate_memory_content(last_message)
                
                # Store the conversation in memory
                self.memory.add(
                    messages=[
                        {"role": "user", "content": sanitized_user_message},
                        {"role": "assistant", "content": sanitized_response}
                    ],
                    user_id=user_id
                )
                
                security_logger.info(f"Successful conversation stored for user {user_id}")
                
            except ValueError as e:
                security_logger.error(f"Failed to store conversation for user {user_id}: {str(e)}")
                # Continue anyway, just don't store in memory
            
            return {
                "messages": [{"role": "assistant", "content": assistant_message}]
            }
            
        except Exception as e:
            security_logger.error(f"Response generation error for user {user_id}: {type(e).__name__}")
            error_message = "I apologize, but I'm experiencing technical difficulties. Please try again later."
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
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == 'quit':
                break
            
            # Basic input validation
            if not user_input:
                print("Please enter a message.")
                continue
                
            if len(user_input) > 10000:
                print("Message too long. Please keep messages under 10,000 characters.")
                continue
            
            # Run the graph
            result = graph.invoke({
                "messages": [{"role": "user", "content": user_input}],
                "user_id": user_id
            })
            
            # Print the response
            if result["messages"]:
                print(f"Assistant: {result['messages'][-1]['content']}\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            security_logger.error(f"Unexpected error in main loop: {type(e).__name__}")
            print("An unexpected error occurred. Please try again.")
            continue

if __name__ == "__main__":
    main()
