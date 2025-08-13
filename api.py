import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from main import MemoryAgent

# Configure logging
security_logger = logging.getLogger('security')

# Configure rate limiting
def get_rate_limits():
    """Get rate limit configuration from environment variables"""
    requests_per_minute = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "20"))
    requests_per_hour = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "100"))
    return requests_per_minute, requests_per_hour

# Initialize rate limiter with in-memory storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=[]  # We'll set limits per endpoint
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., max_length=10000, description="User message")
    user_id: str = Field(..., max_length=100, description="Unique user identifier")

class ChatResponse(BaseModel):
    response: str
    user_id: str
    memory_count: int = 0

class MemorySearchRequest(BaseModel):
    query: str = Field(..., max_length=10000, description="Search query")
    user_id: str = Field(..., max_length=100, description="User identifier")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results")

class MemorySearchResponse(BaseModel):
    memories: List[Dict[str, Any]]
    count: int
    user_id: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Global variables
memory_agent: Optional[MemoryAgent] = None
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global memory_agent, graph
    # Startup
    try:
        memory_agent = MemoryAgent()
        graph = memory_agent.create_graph()
        security_logger.info("MemoryAgent initialized successfully")
    except Exception as e:
        security_logger.error(f"Failed to initialize MemoryAgent: {str(e)}")
        raise RuntimeError(f"Failed to initialize memory agent: {str(e)}")
    
    yield
    
    # Shutdown
    security_logger.info("API server shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Mem0 API",
    description="AI Agent with persistent memory capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_agent():
    """Dependency to get the memory agent instance"""
    global memory_agent, graph
    if memory_agent is None or graph is None:
        raise HTTPException(status_code=500, detail="Memory agent not initialized")
    return memory_agent, graph

@app.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")  # More generous limit for health checks
async def health_check(request: Request):
    """Health check endpoint"""
    try:
        agent, _ = get_agent()
        return HealthResponse(status="healthy", message="API server is running")
    except Exception as e:
        security_logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(lambda: f"{get_rate_limits()[0]}/minute")  # Configurable per minute
@limiter.limit(lambda: f"{get_rate_limits()[1]}/hour")    # Configurable per hour
async def chat(http_request: Request, request: ChatRequest, agent_data=Depends(get_agent)):
    """Main chat endpoint"""
    agent, graph = agent_data
    
    try:
        # Validate input length (additional validation beyond Pydantic)
        if len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Run the graph
        result = graph.invoke({
            "messages": [{"role": "user", "content": request.message}],
            "user_id": request.user_id
        })
        
        # Extract response
        assistant_message = ""
        if result.get("messages"):
            # LangGraph returns AIMessage objects, not dicts
            last_message = result["messages"][-1]
            assistant_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Get memory count
        memory_data = result.get("memory_retrieved", {})
        memory_count = memory_data.get("count", 0)
        
        security_logger.info(f"Successful chat interaction for user {request.user_id}")
        
        return ChatResponse(
            response=assistant_message,
            user_id=request.user_id,
            memory_count=memory_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        security_logger.error(f"Chat error for user {request.user_id}: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your message")

@app.post("/memory/search", response_model=MemorySearchResponse)
@limiter.limit(lambda: f"{get_rate_limits()[0]}/minute")  # Same limits as chat
@limiter.limit(lambda: f"{get_rate_limits()[1]}/hour")
async def search_memory(http_request: Request, request: MemorySearchRequest, agent_data=Depends(get_agent)):
    """Search memories for a user"""
    agent, _ = agent_data
    
    try:
        # Search for memories
        memories_result = agent.memory.search(
            query=request.query, 
            user_id=request.user_id
        )
        
        memories = memories_result.get('results', []) if isinstance(memories_result, dict) else memories_result
        
        # Limit results
        limited_memories = memories[:request.limit] if request.limit else memories
        
        security_logger.info(f"Memory search performed for user {request.user_id}")
        
        return MemorySearchResponse(
            memories=limited_memories,
            count=len(limited_memories),
            user_id=request.user_id
        )
        
    except Exception as e:
        security_logger.error(f"Memory search error for user {request.user_id}: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="An error occurred while searching memories")

@app.delete("/memory/{user_id}")
@limiter.limit("10/minute")  # More restrictive for deletion operations
@limiter.limit("30/hour")
async def clear_memory(http_request: Request, user_id: str, agent_data=Depends(get_agent)):
    """Clear all memories for a user"""
    agent, _ = agent_data
    
    try:
        # Note: mem0 doesn't have a direct clear method, but we can implement it
        # by getting all memories and deleting them
        agent.memory.delete_all(user_id=user_id)
        
        security_logger.info(f"Memory cleared for user {user_id}")
        
        return {"message": f"All memories cleared for user {user_id}"}
        
    except Exception as e:
        security_logger.error(f"Memory clear error for user {user_id}: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="An error occurred while clearing memories")

@app.get("/")
@limiter.limit("30/minute")  # Moderate limit for root endpoint
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": "LangGraph Mem0 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "memory_search": "/memory/search",
            "clear_memory": "/memory/{user_id}"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )