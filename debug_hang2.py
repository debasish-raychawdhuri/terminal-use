#!/usr/bin/env python3
"""
Debug hanging with a running session
"""

import sys
import time
import signal
from terminal_mcp_server.terminal_manager import TerminalManager

def timeout_handler(signum, frame):
    print("TIMEOUT: get_session_state is hanging!")
    sys.exit(1)

def main():
    """Debug get_session with running session."""
    print("Testing get_session with running session...")
    
    terminal_manager = TerminalManager()
    session_id = terminal_manager.generate_session_id()
    
    print(f"Starting vim session {session_id}")
    output, exit_code, running = terminal_manager.run_command(
        "vim -n /tmp/debug_test.txt", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started - Running: {running}")
    
    if running:
        time.sleep(2)  # Let vim initialize
        
        print("About to call get_session_state...")
        
        # Set timeout for get_session_state call
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout for this call
        
        try:
            print("Calling get_session_state...")
            output, exit_code, running = terminal_manager.get_session_state(session_id)
            signal.alarm(0)  # Cancel timeout
            
            print(f"SUCCESS: get_session_state returned")
            print(f"Output length: {len(output)}")
            print(f"Exit code: {exit_code}")
            print(f"Running: {running}")
            
        except Exception as e:
            signal.alarm(0)
            print(f"ERROR in get_session_state: {e}")
        
        print("Terminating session...")
        terminal_manager.terminate_session(session_id)
    else:
        print("Session not running, can't test get_session_state")
    
    print("Test completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
