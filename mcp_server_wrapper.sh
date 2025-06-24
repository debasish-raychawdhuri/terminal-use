#!/bin/bash

# Log file for debugging
LOG_FILE="$(dirname "$0")/mcp_wrapper.log"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Clean start
log "Starting MCP server wrapper"
log "Current directory: $(pwd)"

# Change to the script's directory
cd "$(dirname "$0")"
log "Changed to directory: $(pwd)"

# Kill any existing instances
pkill -f "terminal-mcp-server" 2>/dev/null || true
sleep 1
log "Killed any existing instances"

# Activate virtual environment
if [ -d "./venv" ]; then
  source ./venv/bin/activate
  log "Activated virtual environment"
else
  log "ERROR: Virtual environment not found at ./venv"
  exit 1
fi

# Check if terminal-mcp-server is available
if ! command -v terminal-mcp-server &> /dev/null; then
  log "ERROR: terminal-mcp-server command not found"
  exit 1
fi

# Print MCP server metadata (required by the MCP protocol)
cat << EOF
--- MCP SERVER METADATA ---
{"port": 8000, "protocol": "http", "path": "/", "manifestPath": "/mcp/manifest", "commandPath": "/mcp/command", "eventsPath": "/mcp/events"}
--- END MCP SERVER METADATA ---
EOF

log "Starting server on port 8000"

# Run the server in the foreground
terminal-mcp-server --host 127.0.0.1 --port 8000 --log-level debug 2>> "$LOG_FILE"
