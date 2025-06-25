#!/usr/bin/env python3
"""
Simple test for terminal MCP server functionality
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Test basic functionality."""
    print("Testing basic terminal functionality...")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Test 1: Simple echo command
    print("Test 1: Running echo command...")
    session_id = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "echo 'Hello World'", 
        session_id, 
        timeout=10,
        use_terminal_emulator=False  # Use simple terminal first
    )
    print(f"Output: {output}")
    print(f"Exit code: {exit_code}")
    print(f"Running: {running}")
    
    # Test 2: Interactive command with xterm
    print("\nTest 2: Running vim with xterm...")
    session_id2 = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "vim /tmp/test_file.txt", 
        session_id2, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    print(f"Vim started. Running: {running}")
    
    if running:
        # Send some input
        print("Sending input to vim...")
        terminal_manager.send_input(session_id2, "iHello from vim\x1b:wq\n")
        time.sleep(2)
        
        # Check if still running
        _, _, still_running = terminal_manager.get_session_state(session_id2)
        print(f"Still running after input: {still_running}")
        
        # Terminate if still running
        if still_running:
            terminal_manager.terminate_session(session_id2)
    
    # Check if file was created
    try:
        with open("/tmp/test_file.txt", "r") as f:
            content = f.read()
        print(f"File content: {content}")
    except Exception as e:
        print(f"Could not read file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
