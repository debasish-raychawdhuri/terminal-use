#!/usr/bin/env python3
"""
Clean test for vim without swap file issues
"""

import sys
import time
import os
import tempfile
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Test vim with a clean temporary file."""
    print("Testing vim with clean temporary file...")
    
    # Create a unique temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp_path = tmp.name
    
    print(f"Using temporary file: {tmp_path}")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim with -n flag to avoid swap files
    session_id = terminal_manager.generate_session_id()
    command = f"vim -n {tmp_path}"  # -n flag disables swap files
    
    print(f"Starting: {command}")
    output, exit_code, running = terminal_manager.run_command(
        command, 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Command result - Running: {running}, Exit code: {exit_code}")
    
    if running:
        # Wait for vim to start
        time.sleep(2)
        
        # Get initial state
        print("Getting initial terminal state...")
        output, _, _ = terminal_manager.get_session_state(session_id, raw_output=True)
        print("Raw output length:", len(output))
        print("First 200 chars of output:", repr(output[:200]))
        
        # Enter insert mode
        print("Sending 'i' to enter insert mode...")
        terminal_manager.send_input(session_id, "i")
        time.sleep(1)
        
        # Type text
        text = "Hello how are you"
        print(f"Sending text: '{text}'")
        terminal_manager.send_input(session_id, text)
        time.sleep(1)
        
        # Get state after typing
        print("Getting state after typing...")
        output, _, _ = terminal_manager.get_session_state(session_id, raw_output=True)
        print("Output after typing - length:", len(output))
        print("Last 300 chars:", repr(output[-300:]))
        
        # Exit insert mode
        print("Sending Escape to exit insert mode...")
        terminal_manager.send_input(session_id, "\x1b")
        time.sleep(1)
        
        # Save and quit
        print("Sending ':wq' to save and quit...")
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(2)
        
        # Check if still running
        _, _, still_running = terminal_manager.get_session_state(session_id)
        print(f"Still running after :wq: {still_running}")
        
        if still_running:
            print("Terminating session...")
            terminal_manager.terminate_session(session_id)
    
    # Check file content
    try:
        if os.path.exists(tmp_path):
            with open(tmp_path, "r") as f:
                content = f.read()
            print(f"File content: '{content}'")
            os.unlink(tmp_path)  # Clean up
        else:
            print("File does not exist")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
