#!/usr/bin/env python3
"""
Test script for using vim with xterm through the terminal MCP server
"""

import os
import sys
import time
import tempfile
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Main function to test vim with xterm."""
    print("Testing vim with xterm through terminal MCP server...")
    
    # Create a temporary file
    tmp_path = "/tmp/vim_test_file.txt"
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Run vim with the temporary file
    command = f"vim {tmp_path}"
    session_id = terminal_manager.generate_session_id()
    
    print(f"Starting vim with session ID: {session_id}")
    output, exit_code, running = terminal_manager.run_command(
        command, 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started. Running: {running}")
    
    # Wait a moment for vim to initialize
    time.sleep(2)
    
    # Enter insert mode
    print("Entering insert mode...")
    terminal_manager.send_input(session_id, "i")
    time.sleep(1)
    
    # Type text
    text = "Hello how are you"
    print(f"Typing text: {text}")
    terminal_manager.send_input(session_id, text)
    time.sleep(1)
    
    # Exit insert mode
    print("Exiting insert mode...")
    terminal_manager.send_input(session_id, "\x1b")  # Escape key
    time.sleep(1)
    
    # Save and quit
    print("Saving and quitting...")
    terminal_manager.send_input(session_id, ":wq\n")
    time.sleep(2)
    
    # Check if vim is still running
    _, _, running = terminal_manager.get_session_state(session_id)
    print(f"Vim still running: {running}")
    
    # If vim is still running, terminate it
    if running:
        print("Terminating vim...")
        terminal_manager.terminate_session(session_id)
    
    # Read the content of the file
    try:
        with open(tmp_path, "r") as f:
            content = f.read()
        print(f"Content of the file after editing:\n{content}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
