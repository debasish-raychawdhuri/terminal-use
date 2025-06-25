#!/usr/bin/env python3
"""
Debug the hanging issue with get_session
"""

import sys
import time
import signal
from terminal_mcp_server.terminal_manager import TerminalManager

def timeout_handler(signum, frame):
    print("TIMEOUT: Operation took too long!")
    sys.exit(1)

def main():
    """Debug get_session hanging."""
    print("Testing get_session hanging issue...")
    
    # Set a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    try:
        terminal_manager = TerminalManager()
        session_id = terminal_manager.generate_session_id()
        
        print(f"Starting session {session_id}")
        output, exit_code, running = terminal_manager.run_command(
            "echo 'test'", 
            session_id, 
            timeout=5,
            use_terminal_emulator=True,
            terminal_emulator="xterm"
        )
        
        print(f"Command started - Running: {running}")
        
        if running:
            time.sleep(1)
            
            print("Calling get_session_state...")
            try:
                output, exit_code, running = terminal_manager.get_session_state(session_id)
                print(f"SUCCESS: get_session_state returned")
                print(f"Output length: {len(output)}")
                print(f"Exit code: {exit_code}")
                print(f"Running: {running}")
            except Exception as e:
                print(f"ERROR in get_session_state: {e}")
            
            print("Terminating session...")
            terminal_manager.terminate_session(session_id)
        
        signal.alarm(0)  # Cancel timeout
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")
        signal.alarm(0)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
