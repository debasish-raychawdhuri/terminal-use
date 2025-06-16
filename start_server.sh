#!/bin/bash
# Script to start the Terminal MCP Server

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the package if not already installed
if ! pip show terminal-mcp-server > /dev/null 2>&1; then
    echo "Installing terminal-mcp-server..."
    pip install -e .
fi

# Start the server
echo "Starting Terminal MCP Server..."
terminal-mcp-server --host 0.0.0.0 --port 8000 "$@"
