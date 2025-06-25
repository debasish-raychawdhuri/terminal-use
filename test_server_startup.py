#!/usr/bin/env python3
"""Test server startup and basic functionality."""

import subprocess
import sys
import json
import time
import signal

def test_server_startup():
    """Test that the server starts up correctly."""
    
    print("Testing MCP server startup...")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "terminal_mcp_server.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request)
        print(f"Sending: {request_json}")
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        # Wait for response with timeout
        start_time = time.time()
        response_line = None
        
        while time.time() - start_time < 5:  # 5 second timeout
            if process.poll() is not None:
                print("❌ Process terminated unexpectedly")
                break
                
            try:
                # Try to read a line with a short timeout
                response_line = process.stdout.readline()
                if response_line:
                    break
            except:
                pass
            
            time.sleep(0.1)
        
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"✅ Received response: {json.dumps(response, indent=2)}")
                
                # Send tools/list request
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                request_json = json.dumps(tools_request)
                print(f"Sending tools request: {request_json}")
                
                process.stdin.write(request_json + "\n")
                process.stdin.flush()
                
                # Wait for tools response
                start_time = time.time()
                while time.time() - start_time < 3:
                    tools_response_line = process.stdout.readline()
                    if tools_response_line:
                        tools_response = json.loads(tools_response_line.strip())
                        print(f"✅ Tools response received")
                        
                        if "result" in tools_response and "tools" in tools_response["result"]:
                            tools = tools_response["result"]["tools"]
                            tool_names = [tool["name"] for tool in tools]
                            print(f"Available tools: {tool_names}")
                            
                            if "get_session_html" in tool_names:
                                print("✅ get_session_html tool is available!")
                            else:
                                print("❌ get_session_html tool is missing!")
                        break
                    time.sleep(0.1)
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response_line}")
        else:
            print("❌ No response received within timeout")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()
        
        # Check stderr for any errors
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Stderr output: {stderr_output}")

if __name__ == "__main__":
    test_server_startup()
