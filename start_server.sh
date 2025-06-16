#!/bin/bash
cd /home/debasish/work/talentica/terminal-mcp-server
source venv/bin/activate

# Run in foreground to ensure stdout is visible
terminal-mcp-server --host 0.0.0.0 --port 9118 --log-level debug
