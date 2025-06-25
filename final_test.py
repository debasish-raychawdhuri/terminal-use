#!/usr/bin/env python3
"""
Final test - vim with "Hello how are you"
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Final test."""
    print("=== FINAL TEST: VIM WITH 'Hello how are you' ===")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim
    session_id = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "vim -n /tmp/final_test.txt", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started - Running: {running}")
    
    if running:
        # Wait for vim to initialize
        time.sleep(2)
        
        # Show initial vim screen
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"\n=== INITIAL VIM SCREEN ===")
        print(screen_content)
        print("=== END INITIAL SCREEN ===\n")
        
        # Enter insert mode
        print("Entering insert mode...")
        terminal_manager.send_input(session_id, "i")
        time.sleep(1)
        
        # Type text
        text = "Hello how are you"
        print(f"Typing: '{text}'")
        terminal_manager.send_input(session_id, text)
        time.sleep(1)
        
        # Show screen after typing
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"\n=== SCREEN AFTER TYPING ===")
        print(screen_content)
        print("=== END TYPING SCREEN ===\n")
        
        # Exit and save
        print("Exiting and saving...")
        terminal_manager.send_input(session_id, "\x1b:wq\n")
        time.sleep(2)
        
        # Terminate
        terminal_manager.terminate_session(session_id)
    
    # Check file content
    try:
        with open("/tmp/final_test.txt", "r") as f:
            content = f.read()
        print(f"Final file content: '{content.strip()}'")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
