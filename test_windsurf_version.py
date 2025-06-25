#!/usr/bin/env python3
"""Test what version Windsurf is actually running."""

import subprocess
import sys
import json
import time

def test_windsurf_version():
    """Test the actual version running through the wrapper."""
    
    print("Testing Windsurf wrapper version...")
    
    # Test the run_server.py wrapper directly
    process = subprocess.Popen(
        ["/usr/bin/python", "/home/debasish/work/talentica/terminal-mcp-server/run_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    def send_request(request, timeout=10):
        """Send a request and get response."""
        request_json = json.dumps(request)
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response_line = process.stdout.readline()
            if response_line:
                try:
                    return json.loads(response_line.strip())
                except json.JSONDecodeError:
                    continue
            time.sleep(0.1)
        return None
    
    try:
        # Initialize
        init_response = send_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-windsurf", "version": "1.0.0"}
            }
        })
        
        if not init_response:
            print("❌ Failed to initialize")
            return
        
        print("✅ Server initialized via wrapper")
        
        # Check tools list
        tools_response = send_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        })
        
        if tools_response and "result" in tools_response:
            tools = tools_response["result"]["tools"]
            tool_names = [tool["name"] for tool in tools]
            print(f"Available tools: {tool_names}")
            
            if "get_session_html" in tool_names:
                print("✅ get_session_html tool is available")
                
                # Find the get_session_html tool definition
                html_tool = None
                for tool in tools:
                    if tool["name"] == "get_session_html":
                        html_tool = tool
                        break
                
                if html_tool:
                    description = html_tool.get("description", "")
                    print(f"Tool description: {description}")
                    
                    # Check if the description mentions truncation or limits
                    if "truncation" in description.lower() or "limit" in description.lower():
                        print("❌ Tool description still mentions truncation/limits")
                    else:
                        print("✅ Tool description looks updated")
            else:
                print("❌ get_session_html tool is missing")
        
        # Test with a simple command
        run_response = send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo -e '\\033[31mTest Red\\033[0m \\033[32mTest Green\\033[0m'",
                    "timeout": 10
                }
            }
        })
        
        if run_response and "result" in run_response:
            content = run_response["result"]["content"][0]["text"]
            session_id = None
            for line in content.split("\n"):
                if line.startswith("Session ID:"):
                    session_id = line.split(": ")[1]
                    break
            
            if session_id:
                print(f"✅ Test command executed, session: {session_id}")
                
                # Test get_session_html
                html_response = send_request({
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "get_session_html",
                        "arguments": {
                            "session_id": session_id,
                            "title": "Windsurf Version Test"
                        }
                    }
                }, timeout=15)
                
                if html_response and "result" in html_response:
                    html_content = html_response["result"]["content"][0]["text"]
                    print(f"✅ HTML generated, length: {len(html_content)} characters")
                    
                    # Check for truncation messages
                    if "truncated" in html_content.lower():
                        print("❌ HTML still contains truncation messages!")
                        # Find and show truncation messages
                        lines = html_content.split('\n')
                        for i, line in enumerate(lines):
                            if "truncated" in line.lower():
                                print(f"   Line {i}: {line}")
                    else:
                        print("✅ No truncation messages found")
                    
                    # Check for colors
                    if "color: #800000" in html_content:
                        print("✅ Red color found in HTML")
                    else:
                        print("❌ Red color not found in HTML")
                    
                    if "color: #008000" in html_content:
                        print("✅ Green color found in HTML")
                    else:
                        print("❌ Green color not found in HTML")
                    
                    # Save for inspection
                    with open("windsurf_version_test.html", "w") as f:
                        f.write(html_content)
                    print("✅ HTML saved to windsurf_version_test.html")
                    
                else:
                    print("❌ Failed to get HTML response")
                    print(f"Response: {html_response}")
            else:
                print("❌ Could not extract session ID")
        else:
            print("❌ Failed to run test command")
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()

if __name__ == "__main__":
    test_windsurf_version()
