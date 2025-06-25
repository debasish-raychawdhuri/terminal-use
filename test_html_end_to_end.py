#!/usr/bin/env python3
"""End-to-end test of the HTML functionality."""

import subprocess
import sys
import json
import time

def test_html_functionality():
    """Test the complete HTML functionality."""
    
    print("Testing HTML functionality end-to-end...")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "terminal_mcp_server.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/debasish/work/talentica/terminal-mcp-server"
    )
    
    def send_request(request, timeout=5):
        """Send a request and get response."""
        request_json = json.dumps(request)
        print(f"Sending: {request_json[:100]}...")
        
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
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        
        if not init_response:
            print("❌ Failed to initialize")
            return
        
        print("✅ Server initialized")
        
        # Run a command with colors
        run_response = send_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo -e '\\033[31mRed\\033[0m \\033[32mGreen\\033[0m \\033[1;34mBold Blue\\033[0m'",
                    "timeout": 10
                }
            }
        })
        
        if not run_response or "result" not in run_response:
            print("❌ Failed to run command")
            return
        
        # Extract session ID
        content = run_response["result"]["content"][0]["text"]
        session_id = None
        for line in content.split("\n"):
            if line.startswith("Session ID:"):
                session_id = line.split(": ")[1]
                break
        
        if not session_id:
            print("❌ Could not extract session ID")
            return
        
        print(f"✅ Command executed, session ID: {session_id}")
        
        # Test get_session_html
        html_response = send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_session_html",
                "arguments": {
                    "session_id": session_id,
                    "title": "Test HTML Output"
                }
            }
        }, timeout=10)  # Longer timeout for HTML generation
        
        if not html_response or "result" not in html_response:
            print("❌ Failed to get HTML")
            print(f"Response: {html_response}")
            return
        
        html_content = html_response["result"]["content"][0]["text"]
        
        # Verify HTML content
        if "<!DOCTYPE html>" in html_content and "Red" in html_content:
            print("✅ HTML generated successfully!")
            print(f"HTML length: {len(html_content)} characters")
            
            # Save to file for inspection
            with open("end_to_end_test.html", "w") as f:
                f.write(html_content)
            print("✅ HTML saved to end_to_end_test.html")
            
            # Check for color spans
            if '<span style="color: #800000">Red</span>' in html_content:
                print("✅ Color conversion working correctly!")
            else:
                print("⚠️  Color conversion might have issues")
                print("HTML preview:", html_content[:500])
        else:
            print("❌ HTML content appears invalid")
            print("HTML preview:", html_content[:500])
    
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
    test_html_functionality()
