#!/usr/bin/env python3
"""
Get calculator result quickly
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Get calculator result."""
    terminal_manager = TerminalManager()
    session_id = terminal_manager.generate_session_id()
    
    # Start calculator
    output, exit_code, running = terminal_manager.run_command(
        "terminal_calculator", 
        session_id, 
        timeout=10,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    if running:
        time.sleep(1)
        
        # Enter calculation quickly
        terminal_manager.send_input(session_id, "43.45*55.6\n")
        time.sleep(1)
        
        # Get result screen
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("RESULT SCREEN:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Extract result
        lines = screen.split('\n')
        for line in lines:
            if 'Result:' in line and any(char.isdigit() for char in line):
                print(f"FOUND RESULT: {line}")
        
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
