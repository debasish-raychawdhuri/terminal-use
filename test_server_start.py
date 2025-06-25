#!/usr/bin/env python3
"""
Test MCP server startup with proper initialization
"""

import subprocess
import json
import time
import sys

def test_server():
    """Test MCP server startup."""
    print("Testing MCP server startup...")
    
    # Start server
    cmd = ["python", "terminal_mcp_server/main.py", "--log-level", "INFO"]
    env = {"PYTHONPATH": "."}
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd="/home/debasish/work/talentica/terminal-mcp-server"
    )
    
    try:
        # Send initialize request immediately
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        print("Waiting for response...")
        response = process.stdout.readline()
        
        if response:
            print(f"SUCCESS: Got response: {response.strip()}")
            return True
        else:
            print("ERROR: No response received")
            stderr = process.stderr.read()
            print(f"Stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
