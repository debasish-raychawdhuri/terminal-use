#!/usr/bin/env python3
"""
Test what's causing the MCP server to crash/terminate
"""

import subprocess
import sys
import time
import json

def test_mcp_server_crash():
    """Test if MCP server crashes on get_session."""
    print("Testing MCP server crash on get_session...")
    
    # Start the MCP server
    cmd = ["python", "terminal_mcp_server/main.py"]
    env = {"PYTHONPATH": "."}
    
    print("Starting MCP server...")
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
        # Send initialize request
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
        
        print("Sending initialize...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Init response: {response.strip()}")
        
        # Try to call a tool that creates a session
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo test",
                    "timeout": 5
                }
            }
        }
        
        print("Creating session...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Run command response: {response.strip()}")
        
        # Extract session ID from response
        try:
            resp_data = json.loads(response)
            session_id = resp_data.get("result", {}).get("content", [{}])[0].get("text", "")
            if "Session ID:" in session_id:
                session_id = session_id.split("Session ID:")[1].split()[0]
                print(f"Got session ID: {session_id}")
                
                # Now try get_session - this is where it might crash
                get_session_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "get_session",
                        "arguments": {
                            "session_id": session_id
                        }
                    }
                }
                
                print("Calling get_session (this might crash)...")
                process.stdin.write(json.dumps(get_session_request) + "\n")
                process.stdin.flush()
                
                # Wait for response or crash
                time.sleep(2)
                
                if process.poll() is None:
                    # Still running, try to read response
                    response = process.stdout.readline()
                    print(f"Get session response: {response.strip()}")
                else:
                    print(f"PROCESS CRASHED! Exit code: {process.returncode}")
                    stderr = process.stderr.read()
                    print(f"Error output: {stderr}")
                    
        except Exception as e:
            print(f"Error parsing response: {e}")
        
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_mcp_server_crash()
