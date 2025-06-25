#!/usr/bin/env python3
"""
Test with logging enabled
"""

import logging
import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Test with logging."""
    print("Testing with logging enabled...")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim
    session_id = terminal_manager.generate_session_id()
    print(f"Starting vim with session {session_id}")
    
    output, exit_code, running = terminal_manager.run_command(
        "vim -n /tmp/log_test.txt", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started - Running: {running}")
    
    if running:
        # Wait for vim to initialize
        print("Waiting for vim...")
        time.sleep(3)
        
        # Get session and check screen buffer
        session = terminal_manager.sessions[session_id]
        print(f"Raw buffer length: {len(session.output_buffer)}")
        print(f"Screen buffer content length: {len(session.screen_buffer.get_screen_content())}")
        print(f"Screen buffer raw length: {len(session.screen_buffer.get_raw_buffer())}")
        
        if session.screen_buffer.get_screen_content():
            print("\n=== SCREEN CONTENT ===")
            print(session.screen_buffer.get_screen_content())
            print("=== END SCREEN ===")
        else:
            print("Screen buffer is empty!")
        
        # Terminate
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
