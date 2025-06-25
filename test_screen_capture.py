#!/usr/bin/env python3
"""
Test script to verify screen capture functionality
"""

import sys
import time
import tempfile
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Test screen capture with vim."""
    print("Testing screen capture with vim...")
    
    # Create a unique temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp_path = tmp.name
    
    print(f"Using file: {tmp_path}")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim with no swap file
    session_id = terminal_manager.generate_session_id()
    command = f"vim -n {tmp_path}"
    
    print(f"Starting: {command}")
    output, exit_code, running = terminal_manager.run_command(
        command, 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started - Running: {running}")
    
    if running:
        # Wait for vim to initialize
        print("Waiting for vim to initialize...")
        time.sleep(3)
        
        # Get initial screen
        print("\n=== INITIAL VIM SCREEN ===")
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(screen_content)
        print("=== END INITIAL SCREEN ===\n")
        
        # Enter insert mode
        print("Entering insert mode (pressing 'i')...")
        terminal_manager.send_input(session_id, "i")
        time.sleep(1)
        
        # Get screen after entering insert mode
        print("\n=== SCREEN AFTER ENTERING INSERT MODE ===")
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(screen_content)
        print("=== END INSERT MODE SCREEN ===\n")
        
        # Type text
        text = "Hello how are you"
        print(f"Typing: '{text}'")
        terminal_manager.send_input(session_id, text)
        time.sleep(1)
        
        # Get screen after typing
        print("\n=== SCREEN AFTER TYPING TEXT ===")
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(screen_content)
        print("=== END TYPING SCREEN ===\n")
        
        # Exit insert mode
        print("Exiting insert mode (pressing Escape)...")
        terminal_manager.send_input(session_id, "\x1b")
        time.sleep(1)
        
        # Get screen after exiting insert mode
        print("\n=== SCREEN AFTER EXITING INSERT MODE ===")
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(screen_content)
        print("=== END EXIT INSERT SCREEN ===\n")
        
        # Save and quit
        print("Saving and quitting (:wq)...")
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(2)
        
        # Check if still running
        _, _, still_running = terminal_manager.get_session_state(session_id)
        print(f"Still running after :wq: {still_running}")
        
        if still_running:
            terminal_manager.terminate_session(session_id)
    
    # Check file content
    try:
        with open(tmp_path, "r") as f:
            content = f.read()
        print(f"\nFinal file content: '{content.strip()}'")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
