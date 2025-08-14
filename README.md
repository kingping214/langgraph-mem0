# LangGraph + Mem0 Integration Demo

A demonstration of an AI agent with persistent memory capabilities using LangGraph for workflow orchestration and Mem0 for long-term memory management.

> 🚀 **Quick Start**: Jump to the [Quick Demo section](#-quick-demo-start-here) to see the memory capabilities in action!

## Features

- **Persistent Memory**: Remembers user conversations across sessions using Mem0
- **Contextual Responses**: Retrieves relevant memories to provide personalized interactions
- **Local Embeddings**: Uses Ollama for privacy-focused embedding generation
- **Workflow Orchestration**: LangGraph manages the memory retrieval and response generation flow
- **Multiple Interfaces**: Interactive demos, CLI mode, and REST API

## Architecture

The system consists of two main workflow nodes:

1. **Memory Retrieval**: Searches for relevant past conversations based on the current query
2. **Response Generation**: Uses Claude with memory context to generate personalized responses

```
User Input → Retrieve Memory → Generate Response (with context) → Store New Memory
```

## Quick Start

### Prerequisites

- Python 3.11+ and [UV](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Anthropic API key
- **OR** Docker and Docker Compose (for API server)

### Local Installation (Recommended for Demos)

1. Install UV package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Or on Windows:
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd langgraph-mem0
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Install and set up Ollama:
   ```bash
   # Install Ollama (macOS/Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   ```
   Or download from [https://ollama.ai](https://ollama.ai) for other platforms.

   Then pull the embeddings model:
   ```bash
   ollama pull nomic-embed-text:latest
   ```

5. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and configure all required variables:
   # ANTHROPIC_API_KEY=your_api_key_here
   # ANTHROPIC_MODEL=claude-sonnet-4-0
   # OLLAMA_MODEL=nomic-embed-text:latest
   # OLLAMA_BASE_URL=http://localhost:11434
   # OLLAMA_EMBEDDING_DIMS=768
   # CHROMA_COLLECTION_NAME=test
   # CHROMA_DB_PATH=db
   ```

### Docker Installation (For API Server)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd langgraph-mem0
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your ANTHROPIC_API_KEY
   ```

3. Start the services using Docker Compose:
   ```bash
   # Start all services (API server runs by default)
   docker-compose up -d
   
   # Pull the embedding model (first time only)
   docker-compose run --rm ollama-setup
   
   # View logs
   docker-compose logs -f app
   ```

4. Access the API:
   ```bash
   # API available at http://localhost:8000
   curl http://localhost:8000/health
   
   # Send a chat message
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello!", "user_id": "user123"}'
   ```

5. Stop the services:
   ```bash
   docker-compose down
   ```

## Usage

### 🚀 Quick Demo (Start Here!)

See the memory capabilities in action with the structured demonstration:

```bash
uv run example_demo.py
```

**What this shows:**
- Agent learns user details (name, profession, preferences)
- Demonstrates memory persistence across conversation topics
- Shows contextual recall when asked "What do you remember about me?"
- Choose option 1 for automated demo or option 2 for interactive mode

**Sample interaction:**
```
> "Hi, my name is Alice and I'm a software developer from San Francisco."
< "Nice to meet you, Alice! It's great to connect with a fellow software developer..."

> "What do you remember about me?"
< "I remember that you're Alice, a software developer from San Francisco. You mentioned..."
```

### 🌐 REST API

For integration with other applications:

**Available Endpoints:**
- `GET /health` - Health check
- `POST /chat` - Send chat messages
- `POST /memory/search` - Search user memories  
- `DELETE /memory/{user_id}` - Clear user memories

**Example API Usage:**
```bash
# Health check
curl http://localhost:8000/health

# Chat with the agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hi, my name is Alice", "user_id": "user123"}'

# Search memories
curl -X POST "http://localhost:8000/memory/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "name", "user_id": "user123"}'

# Clear memories
curl -X DELETE "http://localhost:8000/memory/user123"
```

**API Benefits:**
- Rate limiting and security features built-in
- Proper error handling and logging
- Ready for deployment
- Supports multiple concurrent users

**Docker Benefits:**
- **Simplified Setup**: No need to install Python, UV, or Ollama locally
- **Consistent Environment**: Same runtime across all systems
- **Isolation**: Application runs in isolated containers
- **Easy Cleanup**: Remove everything with `docker-compose down`
- **Automatic Ollama Setup**: Embedded model automatically downloads
- **Includes**: API server with health checks and proper error handling

**Note**: Docker setup includes persistent volumes for database and logs, so your data persists between container restarts.

**For learning and demos**, we recommend the local installation to better understand the components.

## Configuration

The memory system is configured in `main.py` with the following components:

- **Embeddings**: Ollama with `nomic-embed-text:latest` model
- **LLM**: Anthropic Claude Sonnet 4.0
- **Vector Store**: ChromaDB (local storage in `db/` directory)
- **Memory Provider**: Mem0 with ChromaDB backend

## Project Structure

```
   main.py              # Core MemoryAgent implementation and CLI
   api.py               # FastAPI server exposing REST API
   example_demo.py      # Demonstration script
   db/                  # ChromaDB vector store data
   logs/                # Security and application logs
   .env.example         # Environment variables template
   pyproject.toml       # Project configuration
   Dockerfile           # Docker container configuration
   docker-compose.yml   # Multi-service Docker setup
   .dockerignore        # Docker build exclusions
   CLAUDE.md           # Development guidance
   SECURITY.md         # Security guidelines
```

## Dependencies

- **LangGraph**: Workflow orchestration and state management
- **Mem0**: Memory management and retrieval
- **Anthropic**: Claude API integration
- **Ollama**: Local embedding generation
- **ChromaDB**: Vector database for memory storage
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **SlowAPI**: Rate limiting middleware

## Rate Limiting

The API includes built-in rate limiting to prevent abuse:

- **Chat/Memory endpoints**: 20 requests/minute, 100 requests/hour (configurable)
- **Health endpoint**: 60 requests/minute 
- **Memory deletion**: 10 requests/minute, 30 requests/hour
- **Uses in-memory storage** - No Redis required
- **Configurable via environment variables**:
  - `RATE_LIMIT_REQUESTS_PER_MINUTE=20`
  - `RATE_LIMIT_REQUESTS_PER_HOUR=100`

## Memory Persistence

Each user is identified by a `user_id`, and all conversations are stored persistently. The agent will:

- Store conversation history automatically
- Retrieve relevant memories for new interactions
- Provide contextual responses based on past conversations
- Maintain separate memory spaces for different users

## Example Memory Scenarios

### Scenario 1: Initial Introduction
```
User: "Hi, my name is Alice and I'm a software developer from San Francisco. 
       I love working with Python and machine learning projects."

Agent: "Nice to meet you, Alice! It's great to connect with a fellow 
        software developer from San Francisco. Python and ML are 
        fascinating fields - what kind of ML projects do you enjoy most?"
```

### Scenario 2: Preference Learning
```
User: "I prefer working in the mornings, usually starting at 7 AM. 
       I'm vegetarian and love Italian cuisine."

Agent: "That's an early start, Alice! Morning productivity can be great. 
        And Italian cuisine has so many wonderful vegetarian options..."
```

### Scenario 3: Memory Recall (Later Session)
```
User: "What do you remember about me?"

Agent: "I remember quite a bit about you, Alice! You're a software 
        developer from San Francisco who loves Python and machine 
        learning projects. You're an early bird who starts work at 7 AM, 
        and you're vegetarian with a preference for Italian cuisine."
```

**Key Demonstration Points:**
- Cross-session memory persistence
- Contextual understanding and recall
- Personalized responses based on learned preferences
- Natural conversation flow with memory integration

## Development

See `CLAUDE.md` for detailed development guidance and architectural information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.