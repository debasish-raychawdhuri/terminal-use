#!/bin/bash

# Log file for debugging
LOG_FILE="$(dirname "$0")/mcp_server.log"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Clean start
log "Starting terminal MCP server"
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

# Check if Python module is available
if ! python -c "import terminal_mcp_server.debug_mcp_server" &> /dev/null; then
  log "ERROR: terminal_mcp_server module not found"
  exit 1
fi

log "Starting MCP server with stdio transport"

# Run the debug server to see what Windsurf is sending
python -m terminal_mcp_server.debug_mcp_server 2>> "$LOG_FILE"
