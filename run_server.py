#!/usr/bin/env python3
"""
Simple wrapper to run the MCP server - for Q CLI compatibility
"""

import os
import sys

# Set up the environment
os.chdir('/home/debasish/work/talentica/terminal-mcp-server')
sys.path.insert(0, '/home/debasish/work/talentica/terminal-mcp-server')

# Import and run the server
from terminal_mcp_server.main import main

if __name__ == "__main__":
    main()
