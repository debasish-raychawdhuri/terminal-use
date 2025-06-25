#!/usr/bin/env python3
"""
Final calculator test
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Final calculator test."""
    terminal_manager = TerminalManager()
    session_id = terminal_manager.generate_session_id()
    
    output, exit_code, running = terminal_manager.run_command(
        "terminal_calculator", 
        session_id, 
        timeout=10,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    if running:
        time.sleep(1)
        
        # Enter the calculation
        terminal_manager.send_input(session_id, "43.45*55.6")
        time.sleep(0.5)
        
        print("After entering calculation:")
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(screen[:500])  # First 500 chars
        
        # Press Enter
        terminal_manager.send_input(session_id, "\n")
        time.sleep(1)
        
        print("\nAfter pressing Enter:")
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        
        # Look for the result
        lines = screen.split('\n')
        for i, line in enumerate(lines):
            if 'Result:' in line:
                print(f"Result line {i}: {line}")
                # Check next few lines for the actual result
                for j in range(i, min(i+3, len(lines))):
                    if any(char.isdigit() for char in lines[j]) and '2417' in lines[j]:
                        print(f"FOUND RESULT: {lines[j]}")
        
        # Calculate expected result for verification
        expected = 43.45 * 55.6
        print(f"Expected result: {expected}")
        
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
