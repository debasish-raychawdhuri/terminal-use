#!/usr/bin/env python3
"""Test the MCP server with the new get_session_html tool."""

import json
import subprocess
import sys
import time
import threading

def test_mcp_server():
    """Test the MCP server functionality."""
    
    # Start the MCP server
    process = subprocess.Popen(
        [sys.executable, "-m", "terminal_mcp_server.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/debasish/work/talentica/terminal-mcp-server"
    )
    
    def send_request(request):
        """Send a JSON-RPC request to the server."""
        request_json = json.dumps(request)
        print(f"Sending: {request_json}")
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Received: {json.dumps(response, indent=2)}")
            return response
        return None
    
    try:
        # Initialize
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
        send_request(init_request)
        
        # Send initialized notification
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "initialized"
        }
        send_request(initialized_request)
        
        # List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = send_request(tools_request)
        
        # Check if get_session_html is in the tools list
        if response and "result" in response:
            tools = response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            print(f"Available tools: {tool_names}")
            
            if "get_session_html" in tool_names:
                print("✅ get_session_html tool is available!")
            else:
                print("❌ get_session_html tool is NOT available!")
        
        # Test running a command with colors
        run_command_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo -e '\\033[31mRed text\\033[0m \\033[32mGreen text\\033[0m'",
                    "timeout": 10
                }
            }
        }
        response = send_request(run_command_request)
        
        # Extract session ID from response
        session_id = None
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            lines = content.split("\n")
            for line in lines:
                if line.startswith("Session ID:"):
                    session_id = line.split(": ")[1]
                    break
        
        if session_id:
            print(f"Got session ID: {session_id}")
            
            # Test get_session_html
            html_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_session_html",
                    "arguments": {
                        "session_id": session_id,
                        "title": "Test Terminal Output"
                    }
                }
            }
            response = send_request(html_request)
            
            if response and "result" in response:
                html_content = response["result"]["content"][0]["text"]
                
                # Save HTML to file
                with open("test_session_output.html", "w") as f:
                    f.write(html_content)
                
                print("✅ HTML generated successfully!")
                print(f"HTML length: {len(html_content)} characters")
                print("Saved to test_session_output.html")
            else:
                print("❌ Failed to generate HTML")
        else:
            print("❌ Could not extract session ID")
    
    except Exception as e:
        print(f"Error during test: {e}")
    
    finally:
        # Clean up
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_server()
