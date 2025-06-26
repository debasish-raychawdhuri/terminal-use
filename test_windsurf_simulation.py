#!/usr/bin/env python3
"""
Simulate exactly what Windsurf is doing to test the live display.
"""

import json
import asyncio
from terminal_mcp_server.main import MCPServer

async def simulate_windsurf_calls():
    """Simulate the exact sequence Windsurf is making."""
    print("=== Simulating Windsurf MCP Calls ===\n")
    
    server = MCPServer()
    
    try:
        # Step 1: Initialize
        print("1. Initialize server...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "windsurf", "version": "1.0.0"}
            }
        }
        response = await server.handle_request(init_request)
        print(f"   Server initialized: {response['result']['serverInfo']['name']}")
        
        # Step 2: Run command (like Windsurf does)
        print("\n2. Run command: ls")
        run_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "ls",
                    "use_terminal_emulator": True
                }
            }
        }
        response = await server.handle_request(run_request)
        output = response['result']['content'][0]['text']
        print(f"   Command executed successfully")
        
        # Extract session ID
        session_id = None
        for line in output.split('\n'):
            if line.startswith('Session ID:'):
                session_id = line.split(': ')[1]
                break
        
        if session_id:
            print(f"   Session ID: {session_id}")
            
            # Step 3: Show live display (like Windsurf does)
            print("\n3. Show live display...")
            live_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "show_session_live",
                    "arguments": {
                        "session_id": session_id,
                        "title": "Terminal Output"
                    }
                }
            }
            response = await server.handle_request(live_request)
            live_output = response['result']['content'][0]['text']
            print(f"   Live display response:")
            print(f"   {live_output}")
            
            # Step 4: Check the actual terminal content
            print("\n4. Check terminal content...")
            session_data = server.terminal_manager.get_session_output(session_id, raw_output=False)
            if session_data:
                print("   Current terminal content:")
                print("   " + "=" * 80)
                for i, line in enumerate(session_data['output'].split('\n')):
                    print(f"   Line {i:2d}: {repr(line)}")
                print("   " + "=" * 80)
            
            # Step 5: Check actual terminal dimensions
            print("\n5. Check terminal dimensions...")
            if session_id in server.terminal_manager.sessions:
                session = server.terminal_manager.sessions[session_id]
                if hasattr(session, 'dimensions'):
                    rows, cols = session.dimensions
                    print(f"   Actual terminal dimensions: {cols}x{rows} (width x height)")
                else:
                    print("   No dimensions found in session")
            
            # Step 6: Test with more commands
            print("\n6. Send more commands to test display...")
            
            # Send a command that shows the prompt clearly
            send_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "send_input",
                    "arguments": {
                        "session_id": session_id,
                        "input": "echo 'Testing first line visibility'\n"
                    }
                }
            }
            response = await server.handle_request(send_request)
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Check content again
            session_data = server.terminal_manager.get_session_output(session_id, raw_output=False)
            if session_data:
                print("   Updated terminal content:")
                print("   " + "=" * 80)
                for i, line in enumerate(session_data['output'].split('\n')):
                    if line.strip():  # Only show non-empty lines
                        print(f"   Line {i:2d}: {repr(line)}")
                print("   " + "=" * 80)
            
            print("\n=== Analysis ===")
            print("Check if the first line (bash prompt) is visible in the live display.")
            print("The live display should show all lines including the initial prompt.")
            
        else:
            print("   ERROR: Could not extract session ID")
        
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        server.live_terminal_manager.cleanup()
        server.terminal_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(simulate_windsurf_calls())
