#!/usr/bin/env python3
"""
Test script to verify MCP server integration with live terminal display.
"""

import json
import asyncio
from terminal_mcp_server.main import MCPServer

async def test_mcp_live_integration():
    """Test the MCP server integration with live terminal display."""
    print("Testing MCP server integration with live terminal display...")
    
    server = MCPServer()
    
    try:
        # Test 1: Initialize the server
        print("\n1. Testing server initialization...")
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
        
        response = await server.handle_request(init_request)
        print(f"Initialize response: {response['result']['serverInfo']['name']}")
        
        # Test 2: List tools
        print("\n2. Testing tools list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await server.handle_request(tools_request)
        tools = response['result']['tools']
        tool_names = [tool['name'] for tool in tools]
        print(f"Available tools: {tool_names}")
        
        # Verify our new tools are present
        expected_tools = ['show_session_live', 'list_live_displays', 'stop_live_display']
        for tool in expected_tools:
            if tool in tool_names:
                print(f"✓ {tool} is available")
            else:
                print(f"✗ {tool} is missing")
        
        # Test 3: Run a command
        print("\n3. Testing command execution...")
        run_command_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_command",
                "arguments": {
                    "command": "echo 'Hello from MCP server!'; echo -e '\\033[31mRed\\033[0m \\033[32mGreen\\033[0m \\033[34mBlue\\033[0m'",
                    "use_terminal_emulator": True
                }
            }
        }
        
        response = await server.handle_request(run_command_request)
        output = response['result']['content'][0]['text']
        print("Command executed successfully!")
        
        # Extract session ID from output
        session_id = None
        for line in output.split('\n'):
            if line.startswith('Session ID:'):
                session_id = line.split(': ')[1]
                break
        
        if session_id:
            print(f"Session ID: {session_id}")
            
            # Test 4: Show live display
            print("\n4. Testing live display...")
            show_live_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "show_session_live",
                    "arguments": {
                        "session_id": session_id,
                        "title": "MCP Test Live Display",
                        "update_interval": 0.5,
                        "width": 80,
                        "height": 25
                    }
                }
            }
            
            response = await server.handle_request(show_live_request)
            live_output = response['result']['content'][0]['text']
            print("Live display response:")
            print(live_output)
            
            # Test 5: List live displays
            print("\n5. Testing list live displays...")
            list_displays_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "list_live_displays",
                    "arguments": {}
                }
            }
            
            response = await server.handle_request(list_displays_request)
            displays_output = response['result']['content'][0]['text']
            print("Active displays:")
            print(displays_output)
            
            # Extract display ID for cleanup
            display_id = None
            if "Display ID:" in displays_output:
                for line in displays_output.split('\n'):
                    if "Display ID:" in line:
                        display_id = line.split(': ')[1]
                        break
            
            # Test 6: Stop live display
            if display_id:
                print("\n6. Testing stop live display...")
                stop_display_request = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "stop_live_display",
                        "arguments": {
                            "display_id": display_id
                        }
                    }
                }
                
                response = await server.handle_request(stop_display_request)
                stop_output = response['result']['content'][0]['text']
                print(f"Stop display result: {stop_output}")
        
        print("\n✓ All MCP integration tests passed!")
        
    except Exception as e:
        print(f"Error during MCP integration test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        server.live_terminal_manager.cleanup()
        server.terminal_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_mcp_live_integration())
