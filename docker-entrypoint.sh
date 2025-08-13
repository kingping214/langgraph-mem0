#!/bin/bash
set -e

# Create necessary directories
mkdir -p /app/db /app/logs

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
    sleep 2
done
echo "Ollama is ready!"

# Check if the embedding model is available
echo "Checking for embedding model..."
if ! curl -s http://ollama:11434/api/tags | grep -q "nomic-embed-text"; then
    echo "Warning: nomic-embed-text model not found. Run 'docker-compose run --rm ollama-setup' to install it."
fi

# Execute the command
exec "$@"