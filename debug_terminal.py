#!/usr/bin/env python3
"""
Debug script to see what raw terminal data we're receiving
"""

import sys
import time
import tempfile
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Debug terminal data capture."""
    print("Debugging terminal data capture...")
    
    # Create a unique temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp_path = tmp.name
    
    print(f"Using file: {tmp_path}")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim
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
        time.sleep(2)
        
        # Get raw data
        print("\n=== RAW TERMINAL DATA ===")
        raw_output = terminal_manager.get_session_state(session_id, raw_output=True)[0]
        print(f"Raw data length: {len(raw_output)}")
        print(f"First 500 chars: {repr(raw_output[:500])}")
        print(f"Last 500 chars: {repr(raw_output[-500:])}")
        print("=== END RAW DATA ===\n")
        
        # Get processed screen content
        print("=== PROCESSED SCREEN CONTENT ===")
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"Screen content length: {len(screen_content)}")
        print(f"Screen content: '{screen_content}'")
        print("=== END PROCESSED CONTENT ===\n")
        
        # Try to get the screen buffer directly from the session
        session = terminal_manager.sessions[session_id]
        if hasattr(session, 'screen_buffer'):
            print("=== SCREEN BUFFER DEBUG ===")
            print(f"Screen buffer raw: {repr(session.screen_buffer.get_raw_buffer()[:200])}")
            print(f"Cursor position: {session.screen_buffer.get_cursor_position()}")
            print("=== END SCREEN BUFFER DEBUG ===\n")
        
        # Terminate
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
