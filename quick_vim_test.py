#!/usr/bin/env python3
"""
Quick vim test - fast screen reading
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Quick vim test."""
    print("Quick vim test starting...")
    
    terminal_manager = TerminalManager()
    session_id = terminal_manager.generate_session_id()
    
    # Start vim
    print("Starting vim...")
    output, exit_code, running = terminal_manager.run_command(
        "vim -n /tmp/quick_test.txt", 
        session_id, 
        timeout=10,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim running: {running}")
    
    if running:
        # Quick check - just 1 second wait
        time.sleep(1)
        
        # Read screen immediately
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("SCREEN CONTENT:")
        print("-" * 40)
        print(screen)
        print("-" * 40)
        
        # Type something quickly
        print("Typing 'i' and 'Hello'...")
        terminal_manager.send_input(session_id, "iHello")
        time.sleep(0.5)  # Just half second
        
        # Read screen again
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("AFTER TYPING:")
        print("-" * 40)
        print(screen)
        print("-" * 40)
        
        # Quick save and exit
        terminal_manager.send_input(session_id, "\x1b:wq\n")
        time.sleep(1)
        
        # Terminate
        terminal_manager.terminate_session(session_id)
    
    # Check file
    try:
        with open("/tmp/quick_test.txt", "r") as f:
            content = f.read()
        print(f"File content: '{content}'")
    except:
        print("No file created")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
