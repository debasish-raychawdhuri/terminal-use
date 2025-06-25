#!/usr/bin/env python3
"""
Utility script to run any command in xterm through the terminal MCP server
"""

import os
import sys
import time
import argparse
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Main function to run a command in xterm."""
    parser = argparse.ArgumentParser(description="Run a command in xterm through terminal MCP server")
    parser.add_argument("command", help="Command to run")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--input", help="Input to send to the command")
    parser.add_argument("--wait", type=int, default=0, help="Time to wait before sending input (seconds)")
    parser.add_argument("--capture-output", action="store_true", help="Capture and display output")
    
    args = parser.parse_args()
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Run command
    session_id = terminal_manager.generate_session_id()
    print(f"Starting command with session ID: {session_id}")
    
    output, exit_code, running = terminal_manager.run_command(
        args.command, 
        session_id, 
        timeout=args.timeout,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Command started. Running: {running}")
    
    # Wait if specified
    if args.wait > 0:
        print(f"Waiting {args.wait} seconds...")
        time.sleep(args.wait)
    
    # Send input if specified
    if args.input:
        print(f"Sending input: {args.input!r}")
        terminal_manager.send_input(session_id, args.input)
    
    # Capture output if requested
    if args.capture_output:
        print("Capturing output...")
        time.sleep(1)  # Give some time for output to be generated
        output, _, _ = terminal_manager.get_session_state(session_id, raw_output=False)
        print("\nOutput:")
        print("=" * 40)
        print(output)
        print("=" * 40)
    
    # Wait for user to terminate
    try:
        print("\nPress Ctrl+C to terminate the command...")
        while terminal_manager.get_session_state(session_id)[2]:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTerminating command...")
        terminal_manager.terminate_session(session_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
