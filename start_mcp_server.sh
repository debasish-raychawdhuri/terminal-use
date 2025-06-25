#!/bin/bash
# MCP Server startup script for Q CLI compatibility

cd /home/debasish/work/talentica/terminal-mcp-server
export PYTHONPATH=/home/debasish/work/talentica/terminal-mcp-server
exec /usr/bin/python3 terminal_mcp_server/main.py "$@"
