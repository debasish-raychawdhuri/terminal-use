#!/usr/bin/env python3
"""
Test interactive session like Windsurf should use.
"""

import json
import asyncio
from terminal_mcp_server.main import MCPServer

async def test_windsurf_interactive():
    """Test interactive session that keeps the prompt visible."""
    print("=== Testing Windsurf Interactive Session ===\n")
    
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
        await server.handle_request(init_request)
        
        # Step 2: Start bash session (not a one-off command)
        print("2. Start interactive bash session...")
        run_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "bash",  # Interactive bash, not a command
                    "use_terminal_emulator": True
                }
            }
        }
        response = await server.handle_request(run_request)
        output = response['result']['content'][0]['text']
        
        # Extract session ID
        session_id = None
        for line in output.split('\n'):
            if line.startswith('Session ID:'):
                session_id = line.split(': ')[1]
                break
        
        print(f"   Interactive bash session started: {session_id}")
        
        # Wait for bash to initialize
        await asyncio.sleep(2)
        
        # Step 3: Show live display
        print("3. Show live display of interactive session...")
        live_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "show_session_live",
                "arguments": {
                    "session_id": session_id,
                    "title": "Interactive Bash Session"
                }
            }
        }
        response = await server.handle_request(live_request)
        live_output = response['result']['content'][0]['text']
        print(f"   Live display started successfully")
        
        # Step 4: Send commands to the interactive session
        print("4. Send commands to interactive session...")
        
        # Send pwd command
        send_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "send_input",
                "arguments": {
                    "session_id": session_id,
                    "input": "pwd\n"
                }
            }
        }
        await server.handle_request(send_request)
        await asyncio.sleep(1)
        
        # Send ls command
        send_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "send_input",
                "arguments": {
                    "session_id": session_id,
                    "input": "ls -la | head -5\n"
                }
            }
        }
        await server.handle_request(send_request)
        await asyncio.sleep(2)
        
        # Step 5: Check the session content
        print("5. Check session content...")
        session_data = server.terminal_manager.get_session_output(session_id, raw_output=False)
        if session_data:
            print("   Session content:")
            print("   " + "=" * 80)
            lines = session_data['output'].split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"   Line {i:2d}: {repr(line)}")
            print("   " + "=" * 80)
        
        print("\n=== Result ===")
        print("This is how Windsurf should use the terminal:")
        print("1. Start an interactive bash session (not one-off commands)")
        print("2. Show live display of the interactive session")
        print("3. Send commands to the session using send_input")
        print("4. The bash prompt should be visible throughout")
        
        print("\nThe live display window should show:")
        print("- Initial bash prompt")
        print("- Commands as they're executed")
        print("- Command output")
        print("- New bash prompt after each command")
        
        print("\nPress Enter to continue...")
        input()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        server.live_terminal_manager.cleanup()
        server.terminal_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_windsurf_interactive())
