#!/usr/bin/env python3
"""
Debug what content is actually being sent to the live display.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager

def debug_live_content():
    """Debug what content is being sent to live display."""
    
    print("=== Debugging Live Display Content ===")
    
    terminal_manager = TerminalManager()
    session_id = None
    
    try:
        # Start bash session
        print("1. Starting bash session...")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        time.sleep(1)
        
        # Send a simple color command
        print("2. Sending color command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRed text\\033[0m'\n")
        time.sleep(2)
        
        # Get the session output (what live display would see)
        print("3. Getting session output...")
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        
        if session_data and 'output' in session_data:
            content = session_data['output']
            print(f"Content length: {len(content)}")
            print(f"Content (first 500 chars): {repr(content[:500])}")
            
            # Look for escape sequences
            literal_escapes = content.count('\\033')
            actual_escapes = content.count('\x1b')
            
            print(f"\nEscape sequence analysis:")
            print(f"  Literal \\033 sequences: {literal_escapes}")
            print(f"  Actual \\x1b sequences: {actual_escapes}")
            
            # Show line by line
            print(f"\nContent line by line:")
            lines = content.split('\n')
            for i, line in enumerate(lines[:10]):  # Show first 10 lines
                if line.strip():
                    has_literal = '\\033' in line
                    has_actual = '\x1b' in line
                    print(f"  Line {i}: {repr(line[:80])} {'(LITERAL)' if has_literal else ''} {'(ACTUAL)' if has_actual else ''}")
        
    finally:
        if session_id:
            terminal_manager.terminate_session(session_id)

if __name__ == "__main__":
    debug_live_content()
