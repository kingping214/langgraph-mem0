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

**Install dependencies:**
```bash
uv sync
```

**Run the main interactive demo:**
```bash
python main.py
```

**Run the example demonstration script:**
```bash
python example_demo.py
```

## Key Files

- `main.py` - Core MemoryAgent implementation and interactive CLI
- `example_demo.py` - Demonstration script showing memory capabilities
- `db/` - ChromaDB vector store data (auto-created)
- `pyproject.toml` - Project dependencies and configuration

## Memory Configuration

The memory system is fully configurable via required environment variables in `MemoryAgent.__init__()`:
- **Ollama embeddings**: Model, base URL, and dimensions via `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, and `OLLAMA_EMBEDDING_DIMS`
- **Anthropic LLM**: Model via `ANTHROPIC_MODEL`
- **ChromaDB vector store**: Database path and collection name via `CHROMA_DB_PATH` and `CHROMA_COLLECTION_NAME`

All configuration must be specified via environment variables - no defaults are provided to ensure explicit configuration.

## Dependencies

Key dependencies include:
- `langgraph>=0.2.0` - Workflow orchestration
- `mem0ai>=0.1.0` - Memory management
- `anthropic>=0.34.0` - Claude API client
- `ollama>=0.5.3` - Local embeddings
- `chromadb>=1.0.16` - Vector database