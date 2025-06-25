#!/usr/bin/env python3
"""
Direct test of terminal MCP server with vim
"""

import os
import sys
import time
import tempfile
from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.terminal_emulator import detect_terminal_emulator

def main():
    """Main function to test terminal MCP server with vim."""
    print("Testing terminal MCP server with vim...")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp_path = tmp.name
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Detect terminal emulator
    emulator = detect_terminal_emulator()
    print(f"Using terminal emulator: {emulator}")
    
    # Run vim with the temporary file
    command = f"vim -c 'normal iHello how are you' -c 'wq' {tmp_path}"
    session_id = terminal_manager.generate_session_id()
    
    print(f"Running command: {command}")
    output, exit_code, running = terminal_manager.run_command(
        command, 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator=emulator
    )
    
    print(f"Command executed. Exit code: {exit_code}, Running: {running}")
    
    # Wait for the command to complete
    while running:
        print("Waiting for command to complete...")
        time.sleep(1)
        _, exit_code, running = terminal_manager.get_session_state(session_id)
    
    # Read the content of the file
    try:
        with open(tmp_path, "r") as f:
            content = f.read()
        print(f"Content of the file after editing:\n{content}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    # Clean up
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
