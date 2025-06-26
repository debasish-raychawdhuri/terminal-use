#!/usr/bin/env python3
"""
Capture exactly what's being displayed to diagnose the issue.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager

def capture_display_content():
    """Capture and show exactly what would be displayed."""
    
    print("=== Capturing Display Content ===")
    
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
        
        # Send simple color command
        print("2. Sending color command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRed\\033[0m'\n")
        time.sleep(2)
        
        # Get what the live display would see
        print("3. Getting display content...")
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        
        if session_data and 'output' in session_data:
            content = session_data['output']
            
            print(f"Content length: {len(content)}")
            print(f"Content type: {type(content)}")
            
            # Show the exact content that would go to the terminal emulator
            print("\n--- EXACT CONTENT THAT GOES TO TERMINAL EMULATOR ---")
            print(repr(content))
            
            # Show it line by line
            print("\n--- LINE BY LINE BREAKDOWN ---")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"Line {i}: {repr(line)}")
            
            # Check for different types of escape sequences
            print("\n--- ESCAPE SEQUENCE ANALYSIS ---")
            literal_033 = content.count('\\033')
            actual_x1b = content.count('\x1b')
            literal_x1b = content.count('\\x1b')
            
            print(f"Literal \\033 sequences: {literal_033}")
            print(f"Actual \\x1b sequences: {actual_x1b}")
            print(f"Literal \\x1b sequences: {literal_x1b}")
            
            if actual_x1b > 0:
                print("✅ Content has actual ANSI escape sequences")
                
                # Find and show the actual escape sequences
                import re
                ansi_pattern = r'\x1b\[[0-9;]*[a-zA-Z]'
                matches = re.findall(ansi_pattern, content)
                print(f"Found ANSI sequences: {matches}")
                
            elif literal_033 > 0:
                print("❌ Content only has literal \\033 sequences (not processed)")
            else:
                print("❌ Content has no escape sequences at all")
        
        # Also check direct session access
        print("\n--- DIRECT SESSION ACCESS ---")
        if session_id in terminal_manager.sessions:
            session = terminal_manager.sessions[session_id]
            
            # Check TUI detection
            is_tui = terminal_manager._is_tui_active(session)
            print(f"TUI detected: {is_tui}")
            
            # Get raw vs processed
            raw_output = session.get_output(raw=True)
            processed_output = session.get_output(raw=False)
            
            print(f"Raw output length: {len(raw_output)}")
            print(f"Processed output length: {len(processed_output)}")
            
            raw_escapes = raw_output.count('\x1b')
            processed_escapes = processed_output.count('\x1b')
            
            print(f"Raw output ANSI sequences: {raw_escapes}")
            print(f"Processed output ANSI sequences: {processed_escapes}")
            
            if raw_escapes > 0:
                print("✅ Raw output has ANSI sequences")
                # Show a sample
                print(f"Raw output sample: {repr(raw_output[:200])}")
            else:
                print("❌ Raw output has no ANSI sequences")
        
    finally:
        if session_id:
            terminal_manager.terminate_session(session_id)
    
    print("\n=== Analysis Complete ===")
    print("This shows exactly what content is being sent to the terminal emulator.")
    print("If you see literal \\033 instead of \\x1b, that's the problem.")

if __name__ == "__main__":
    capture_display_content()
