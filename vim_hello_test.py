#!/usr/bin/env python3
"""
Test vim with "Hello how are you" text
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Test vim with specific text."""
    print("Opening vim and writing 'Hello how are you'...")
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim
    session_id = terminal_manager.generate_session_id()
    output, exit_code, running = terminal_manager.run_command(
        "vim /tmp/hello_test.txt", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"Vim started. Running: {running}")
    
    if running:
        # Wait for vim to initialize
        time.sleep(1)
        
        # Enter insert mode
        print("Entering insert mode...")
        terminal_manager.send_input(session_id, "i")
        time.sleep(0.5)
        
        # Type the text
        text = "Hello how are you"
        print(f"Typing: '{text}'")
        terminal_manager.send_input(session_id, text)
        time.sleep(0.5)
        
        # Get current output/screen content
        print("\nCurrent terminal output:")
        print("=" * 50)
        output, _, _ = terminal_manager.get_session_state(session_id, raw_output=False)
        print(output)
        print("=" * 50)
        
        # Exit insert mode and save
        print("\nExiting insert mode and saving...")
        terminal_manager.send_input(session_id, "\x1b:wq\n")
        time.sleep(2)
        
        # Check final state
        _, _, still_running = terminal_manager.get_session_state(session_id)
        print(f"Still running: {still_running}")
        
        if still_running:
            terminal_manager.terminate_session(session_id)
    
    # Verify file content
    try:
        with open("/tmp/hello_test.txt", "r") as f:
            content = f.read()
        print(f"\nFile content: '{content.strip()}'")
    except Exception as e:
        print(f"Could not read file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
