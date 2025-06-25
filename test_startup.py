#!/usr/bin/env python3
"""
Test MCP server startup to see where it hangs
"""

import sys
import os
sys.path.insert(0, '/home/debasish/work/talentica/terminal-mcp-server')

print("Starting MCP server test...")

try:
    print("1. Importing main module...")
    from terminal_mcp_server.main import main
    
    print("2. Import successful, calling main()...")
    main()
    
except KeyboardInterrupt:
    print("3. Interrupted by user")
except Exception as e:
    print(f"3. Error: {e}")
    import traceback
    traceback.print_exc()
