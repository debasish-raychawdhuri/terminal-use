#!/usr/bin/env python3
"""
Manually process the raw terminal data through screen buffer
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Manually process raw data."""
    print("Manual processing test...")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim
    session_id = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "vim -n /tmp/manual_test.txt", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started - Running: {running}")
    
    if running:
        # Wait for vim to initialize
        time.sleep(2)
        
        # Get the session and raw data
        session = terminal_manager.sessions[session_id]
        raw_data = session.output_buffer
        
        print(f"Raw data length: {len(raw_data)}")
        
        # Manually process the raw data through a new screen buffer
        from terminal_mcp_server.screen_buffer import TerminalScreenBuffer
        manual_buffer = TerminalScreenBuffer(40, 100)
        manual_buffer.process_data(raw_data)
        
        content = manual_buffer.get_screen_content()
        print(f"\n=== MANUALLY PROCESSED SCREEN ===")
        print(content)
        print("=== END MANUAL SCREEN ===\n")
        
        # Compare with session's screen buffer
        session_content = session.screen_buffer.get_screen_content()
        print(f"Session screen buffer content: '{session_content}'")
        
        # Terminate
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
