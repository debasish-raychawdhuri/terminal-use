#!/usr/bin/env python3
"""
Simple debug to check screen buffer creation
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Simple debug."""
    print("Simple debug test...")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start a simple command first
    session_id = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "echo 'test'", 
        session_id, 
        timeout=10,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Echo command - Running: {running}, Exit: {exit_code}")
    
    # Check if session has screen buffer
    session = terminal_manager.sessions[session_id]
    print(f"Session type: {type(session)}")
    print(f"Has screen_buffer: {hasattr(session, 'screen_buffer')}")
    
    if hasattr(session, 'screen_buffer'):
        print(f"Screen buffer type: {type(session.screen_buffer)}")
        # Test the screen buffer directly
        session.screen_buffer.process_data("Direct test")
        content = session.screen_buffer.get_screen_content()
        print(f"Direct test content: '{content}'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
