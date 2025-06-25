#!/usr/bin/env python3
"""Debug script to help identify Windsurf hanging issues."""

import subprocess
import sys
import json
import time
import os

def create_minimal_server():
    """Create a minimal MCP server for testing."""
    minimal_server = '''#!/usr/bin/env python3
import json
import sys

def main():
    """Minimal MCP server."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            req_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "minimal-test", "version": "1.0.0"}
                    }
                }
                print(json.dumps(response), flush=True)
            
            elif method == "initialized":
                # Notification, no response
                pass
            
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [{
                            "name": "test_tool",
                            "description": "A test tool",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            }
                        }]
                    }
                }
                print(json.dumps(response), flush=True)
            
            elif method == "tools/call":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": "Test tool executed successfully!"
                        }]
                    }
                }
                print(json.dumps(response), flush=True)
                
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": req_id if 'req_id' in locals() else None,
                "error": {"code": -32000, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
'''
    
    with open("minimal_mcp_server.py", "w") as f:
        f.write(minimal_server)
    
    os.chmod("minimal_mcp_server.py", 0o755)
    print("✅ Created minimal_mcp_server.py")

def test_minimal_server():
    """Test the minimal server."""
    print("Testing minimal MCP server...")
    
    process = subprocess.Popen(
        [sys.executable, "minimal_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print("✅ Minimal server responds to initialization")
        else:
            print("❌ Minimal server does not respond")
            
    finally:
        process.terminate()

def create_windsurf_config():
    """Create a Windsurf configuration for testing."""
    config = {
        "mcpServers": {
            "terminal-minimal": {
                "command": "/usr/bin/python",
                "args": ["/home/debasish/work/talentica/terminal-mcp-server/minimal_mcp_server.py"]
            },
            "terminal-full": {
                "command": "/usr/bin/python",
                "args": ["/home/debasish/work/talentica/terminal-mcp-server/run_server.py"]
            }
        }
    }
    
    with open("windsurf_test_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created windsurf_test_config.json")
    print("To test in Windsurf:")
    print("1. First try the minimal server configuration")
    print("2. If that works, try the full server configuration")
    print("3. Check Windsurf logs for any error messages")

def check_dependencies():
    """Check if all dependencies are available."""
    print("Checking dependencies...")
    
    try:
        import pexpect
        print("✅ pexpect is available")
    except ImportError:
        print("❌ pexpect is not available - install with: pip install pexpect")
    
    # Check if the main module can be imported
    try:
        sys.path.insert(0, '/home/debasish/work/talentica/terminal-mcp-server')
        from terminal_mcp_server.main import main
        print("✅ Main module imports successfully")
    except Exception as e:
        print(f"❌ Main module import failed: {e}")
    
    # Check if ANSI converter works
    try:
        from terminal_mcp_server.ansi_to_html import convert_ansi_to_html
        test_html = convert_ansi_to_html("test", "test")
        print("✅ ANSI to HTML converter works")
    except Exception as e:
        print(f"❌ ANSI converter failed: {e}")

def main():
    """Run all diagnostic tests."""
    print("=== Windsurf MCP Server Diagnostic ===\n")
    
    check_dependencies()
    print()
    
    create_minimal_server()
    test_minimal_server()
    print()
    
    create_windsurf_config()
    print()
    
    print("=== Troubleshooting Tips ===")
    print("1. If Windsurf hangs on the full server:")
    print("   - Try the minimal server first")
    print("   - Check Windsurf developer console for errors")
    print("   - Look for timeout or memory issues")
    print()
    print("2. Common issues:")
    print("   - Large HTML output causing browser hang")
    print("   - Infinite loops in ANSI processing")
    print("   - Memory usage from large terminal buffers")
    print()
    print("3. The current implementation has safety limits:")
    print("   - Max 50KB input text")
    print("   - Max 100KB HTML output")
    print("   - Max 1000 lines processed")
    print("   - Timeout protection on processing loops")

if __name__ == "__main__":
    main()
