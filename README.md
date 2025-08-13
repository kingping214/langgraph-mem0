# LangGraph + Mem0 Integration Demo

A demonstration of an AI agent with persistent memory capabilities using LangGraph for workflow orchestration and Mem0 for long-term memory management.

## Features

- **Persistent Memory**: Remembers user conversations across sessions using Mem0
- **Contextual Responses**: Retrieves relevant memories to provide personalized interactions
- **Local Embeddings**: Uses Ollama for privacy-focused embedding generation
- **Workflow Orchestration**: LangGraph manages the memory retrieval and response generation flow
- **Multiple Interfaces**: Both interactive CLI and demonstration scripts available

## Architecture

The system consists of two main workflow nodes:

1. **Memory Retrieval**: Searches for relevant past conversations based on the current query
2. **Response Generation**: Uses Claude with memory context to generate personalized responses

```
User Input → Retrieve Memory → Generate Response (with context) → Store New Memory
```

## Setup

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/getting-started/installation/) package manager
- [Ollama](https://ollama.ai/) installed and running
- Anthropic API key

### Installation

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

## Usage

### Interactive Mode

Run the main interactive demo:

```bash
python main.py
```

This starts a conversational interface where the agent will remember your preferences and past interactions across sessions.

### Example Demonstration

Run the structured demo to see memory capabilities:

```bash
python example_demo.py
```

Choose option 1 for an automated demo or option 2 for interactive mode.

## Configuration

The memory system is configured in `main.py` with the following components:

- **Embeddings**: Ollama with `nomic-embed-text:latest` model
- **LLM**: Anthropic Claude Sonnet 4.0
- **Vector Store**: ChromaDB (local storage in `db/` directory)
- **Memory Provider**: Mem0 with ChromaDB backend

## Project Structure

```
   main.py              # Core MemoryAgent implementation
   example_demo.py      # Demonstration script
   db/                  # ChromaDB vector store data
   .env.example         # Environment variables template
   pyproject.toml       # Project configuration
   CLAUDE.md           # Development guidance
```

## Dependencies

- **LangGraph**: Workflow orchestration and state management
- **Mem0**: Memory management and retrieval
- **Anthropic**: Claude API integration
- **Ollama**: Local embedding generation
- **ChromaDB**: Vector database for memory storage

## Memory Persistence

Each user is identified by a `user_id`, and all conversations are stored persistently. The agent will:

- Store conversation history automatically
- Retrieve relevant memories for new interactions
- Provide contextual responses based on past conversations
- Maintain separate memory spaces for different users

## Example Interactions

The demo showcases scenarios like:

1. **User introduces themselves**: "Hi, my name is Alice and I'm a software developer from San Francisco."
2. **Agent remembers later**: When asked "What do you remember about me?", the agent recalls name, profession, and location.
3. **Contextual responses**: Future conversations reference past preferences and information.

## Development

See `CLAUDE.md` for detailed development guidance and architectural information.

## License

This project is licensed under the terms specified in the LICENSE file.