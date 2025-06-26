#!/usr/bin/env python3
"""
Debug raw output to see if ANSI sequences are being captured.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager

def debug_raw_output():
    """Debug raw output capture."""
    
    print("=== Debugging Raw Output Capture ===")
    
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
        
        # Get both raw and processed output
        print("3. Getting outputs...")
        
        # Raw output
        raw_data = terminal_manager.get_session_output(session_id, raw_output=True)
        processed_data = terminal_manager.get_session_output(session_id, raw_output=False)
        
        if raw_data and 'output' in raw_data:
            raw_content = raw_data['output']
            print(f"Raw output length: {len(raw_content)}")
            print(f"Raw output (first 200 chars): {repr(raw_content[:200])}")
            
            # Count escape sequences
            literal_escapes = raw_content.count('\\033')
            actual_escapes = raw_content.count('\x1b')
            print(f"Raw - Literal \\033: {literal_escapes}, Actual \\x1b: {actual_escapes}")
        
        if processed_data and 'output' in processed_data:
            processed_content = processed_data['output']
            print(f"\nProcessed output length: {len(processed_content)}")
            print(f"Processed output (first 200 chars): {repr(processed_content[:200])}")
            
            # Count escape sequences
            literal_escapes = processed_content.count('\\033')
            actual_escapes = processed_content.count('\x1b')
            print(f"Processed - Literal \\033: {literal_escapes}, Actual \\x1b: {actual_escapes}")
        
        # Direct access to session object
        print("\n4. Direct session access...")
        if session_id in terminal_manager.sessions:
            session = terminal_manager.sessions[session_id]
            
            direct_raw = session.get_output(raw=True)
            direct_processed = session.get_output(raw=False)
            
            print(f"Direct raw length: {len(direct_raw)}")
            print(f"Direct raw (first 200 chars): {repr(direct_raw[:200])}")
            
            actual_escapes_direct = direct_raw.count('\x1b')
            print(f"Direct raw - Actual \\x1b: {actual_escapes_direct}")
            
            if actual_escapes_direct > 0:
                print("✅ Raw output DOES contain ANSI escape sequences!")
            else:
                print("❌ Raw output does NOT contain ANSI escape sequences")
        
    finally:
        if session_id:
            terminal_manager.terminate_session(session_id)

if __name__ == "__main__":
    debug_raw_output()
