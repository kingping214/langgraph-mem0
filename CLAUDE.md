# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph + Mem0 integration demo that showcases an AI agent with persistent memory capabilities. The agent uses:
- **LangGraph** for workflow orchestration
- **Mem0** for long-term memory storage and retrieval
- **Anthropic Claude** as the primary LLM
- **Ollama** for local embeddings (nomic-embed-text)
- **ChromaDB** as the vector store backend

## Architecture

The main architecture consists of a `MemoryAgent` class that creates a LangGraph workflow with two key nodes:
1. `retrieve_memory` - Searches for relevant memories from past conversations
2. `generate_response` - Generates responses using Claude with memory context

The agent maintains persistent memory per user_id across sessions, storing conversation history and automatically retrieving relevant context for new interactions.

## Setup Requirements

Before running the application:
1. Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY`
2. Ensure Ollama is running locally on port 11434 with the `nomic-embed-text:latest` model
3. Install dependencies using `uv`

## Common Commands

### Local Development (Recommended for Demos)

**Install dependencies:**
```bash
uv sync
```

**Run the example demonstration script (start here!):**
```bash
uv run example_demo.py
```


### Docker Development (API Server)

**Start all services (API server runs by default):**
```bash
docker-compose up -d
```

**Setup Ollama model (first time):**
```bash
docker-compose run --rm ollama-setup
```

**API will be available at:** `http://localhost:8000`

**API Endpoints:**
- `GET /health` - Health check
- `POST /chat` - Send chat messages
- `POST /memory/search` - Search user memories
- `DELETE /memory/{user_id}` - Clear user memories

**Example API usage:**
```bash
# Check API health
curl http://localhost:8000/health

# Send a chat message
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "user_id": "user123"}'

# Search memories
curl -X POST "http://localhost:8000/memory/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "previous conversations", "user_id": "user123"}'
```


**Run example demo (local development only):**
```bash
# Note: example_demo.py is designed for local development
# For Docker users, use the API instead
```

**View logs:**
```bash
docker-compose logs -f app
```

**Stop services:**
```bash
docker-compose down
```

## Key Files

- `main.py` - Core MemoryAgent implementation
- `api.py` - FastAPI server exposing the MemoryAgent as REST API
- `example_demo.py` - Demonstration script showing memory capabilities (local only)
- `db/` - ChromaDB vector store data (auto-created)
- `pyproject.toml` - Project dependencies and configuration
- `Dockerfile` - Container configuration for API server
- `docker-compose.yml` - Multi-service Docker setup with Ollama
- `.dockerignore` - Docker build exclusions
- `SECURITY.md` - Security guidelines and configuration documentation
- `security.log` - Security events and monitoring log (auto-created)

## Memory Configuration

The memory system is fully configurable via required environment variables in `MemoryAgent.__init__()`:
- **Ollama embeddings**: Model, base URL, and dimensions via `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, and `OLLAMA_EMBEDDING_DIMS`
- **Anthropic LLM**: Model via `ANTHROPIC_MODEL`
- **ChromaDB vector store**: Database path and collection name via `CHROMA_DB_PATH` and `CHROMA_COLLECTION_NAME`

All configuration must be specified via environment variables - no defaults are provided to ensure explicit configuration.

## Security Features

The application implements multiple security layers:

- **Input Validation**: All user inputs are sanitized and validated to prevent injection attacks
- **Rate Limiting**: Configurable per-IP rate limiting (see Rate Limiting section below)
- **Environment Security**: Mandatory validation of all configuration variables
- **Error Handling**: Secure error messages that don't expose system internals
- **Memory Protection**: Content validation before storage to prevent malicious data persistence
- **Security Logging**: Comprehensive monitoring and alerting for security events

See `SECURITY.md` for detailed security configuration and best practices.

## Dependencies

Key dependencies include:
- `langgraph>=0.2.0` - Workflow orchestration
- `mem0ai>=0.1.0` - Memory management
- `anthropic>=0.34.0` - Claude API client
- `ollama>=0.5.3` - Local embeddings
- `chromadb>=1.0.16` - Vector database
- `fastapi>=0.104.0` - REST API framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `slowapi>=0.1.9` - Rate limiting middleware

## Rate Limiting

The API includes configurable rate limiting to prevent abuse:

### Default Limits
- **Chat/Memory endpoints**: 20 requests/minute, 100 requests/hour
- **Health endpoint**: 60 requests/minute (more generous)
- **Memory deletion**: 10 requests/minute, 30 requests/hour (more restrictive)
- **Root endpoint**: 30 requests/minute

### Configuration
Rate limits can be configured via environment variables:
- `RATE_LIMIT_REQUESTS_PER_MINUTE` (default: 20)
- `RATE_LIMIT_REQUESTS_PER_HOUR` (default: 100)

### Implementation
- Uses in-memory storage (no Redis required)
- Rate limiting is applied per IP address
- Returns HTTP 429 when limits are exceeded