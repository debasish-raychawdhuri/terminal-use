#!/bin/bash

# Wrapper script for terminal MCP server to ensure xterm is used

# Check if xterm is available
if command -v xterm &> /dev/null; then
    echo "Using xterm as terminal emulator"
    export TERMINAL_EMULATOR=xterm
else
    echo "xterm not found, using default terminal emulator"
fi

# Start the MCP server
python3 mcp_server_standalone.py "$@"
