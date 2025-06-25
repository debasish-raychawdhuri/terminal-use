#!/usr/bin/env python3
"""Test full color rendering without truncation."""

import subprocess
import sys
import json
import time

def test_full_color_rendering():
    """Test that colors are fully preserved without truncation."""
    
    print("Testing full color rendering...")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "terminal_mcp_server.main"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/debasish/work/talentica/terminal-mcp-server"
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
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        
        if not init_response:
            print("❌ Failed to initialize")
            return
        
        print("✅ Server initialized")
        
        # Run a command with lots of colors
        colorful_command = """
echo -e "\\033[31mRed\\033[0m \\033[32mGreen\\033[0m \\033[33mYellow\\033[0m \\033[34mBlue\\033[0m \\033[35mMagenta\\033[0m \\033[36mCyan\\033[0m"
echo -e "\\033[1;31mBold Red\\033[0m \\033[1;32mBold Green\\033[0m \\033[1;33mBold Yellow\\033[0m"
echo -e "\\033[41mRed BG\\033[0m \\033[42mGreen BG\\033[0m \\033[43mYellow BG\\033[0m"
echo -e "\\033[38;5;196mBright Red (256)\\033[0m \\033[38;5;46mBright Green (256)\\033[0m"
echo -e "\\033[38;2;255;165;0mOrange RGB\\033[0m \\033[38;2;128;0;128mPurple RGB\\033[0m"
echo -e "\\033[1;4;31mBold Underlined Red\\033[0m \\033[3;32mItalic Green\\033[0m"
echo -e "\\033[7;36mReverse Cyan\\033[0m \\033[9;35mStrikethrough Magenta\\033[0m"
""".strip()
        
        run_response = send_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": colorful_command,
                    "timeout": 15
                }
            }
        })
        
        if not run_response or "result" not in run_response:
            print("❌ Failed to run colorful command")
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
        
        print(f"✅ Colorful command executed, session ID: {session_id}")
        
        # Wait a moment for command to complete
        time.sleep(2)
        
        # Test get_session_html with full output
        html_response = send_request({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_session_html",
                "arguments": {
                    "session_id": session_id,
                    "title": "Full Color Test"
                }
            }
        }, timeout=15)
        
        if not html_response or "result" not in html_response:
            print("❌ Failed to get HTML")
            print(f"Response: {html_response}")
            return
        
        html_content = html_response["result"]["content"][0]["text"]
        
        # Verify HTML content has colors
        color_checks = [
            ("#800000", "Dark Red"),
            ("#008000", "Dark Green"), 
            ("#808000", "Dark Yellow"),
            ("#000080", "Dark Blue"),
            ("#800080", "Dark Magenta"),
            ("#008080", "Dark Cyan"),
            ("font-weight: bold", "Bold formatting"),
            ("text-decoration: underline", "Underline formatting"),
            ("font-style: italic", "Italic formatting"),
            ("background-color:", "Background colors"),
            ("#ff0000", "Bright colors"),
            ("#ff6500", "RGB colors")  # Orange RGB should be close to this
        ]
        
        found_colors = 0
        for color_code, description in color_checks:
            if color_code in html_content:
                print(f"✅ Found {description}: {color_code}")
                found_colors += 1
            else:
                print(f"❌ Missing {description}: {color_code}")
        
        print(f"\n✅ HTML generated successfully!")
        print(f"HTML length: {len(html_content)} characters")
        print(f"Colors found: {found_colors}/{len(color_checks)}")
        
        # Save to file for inspection
        with open("full_color_test.html", "w") as f:
            f.write(html_content)
        print("✅ HTML saved to full_color_test.html")
        
        # Check if any truncation messages exist
        if "truncated" in html_content.lower():
            print("❌ Found truncation in HTML output!")
        else:
            print("✅ No truncation found - full output preserved!")
    
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
    test_full_color_rendering()
