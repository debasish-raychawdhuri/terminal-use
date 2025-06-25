#!/usr/bin/env python3
"""
Vim demonstration - open vim, type text, save file, show screen content
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Demonstrate vim functionality with screen capture."""
    print("🚀 VIM DEMONSTRATION - Opening vim, typing text, and saving file")
    print("=" * 70)
    
    # Initialize terminal manager
    terminal_manager = TerminalManager()
    
    # Start vim with a new file
    session_id = terminal_manager.generate_session_id()
    filename = "/tmp/vim_demo_file.txt"
    
    print(f"📝 Opening vim with file: {filename}")
    output, exit_code, running = terminal_manager.run_command(
        f"vim -n {filename}", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"✅ Vim started successfully - Running: {running}")
    
    if running:
        # Wait for vim to fully initialize
        print("⏳ Waiting for vim to initialize...")
        time.sleep(2)
        
        # Show initial vim screen
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"\n📺 INITIAL VIM SCREEN:")
        print("=" * 50)
        print(screen_content)
        print("=" * 50)
        
        # Enter insert mode
        print("\n🔤 Entering insert mode (pressing 'i')...")
        terminal_manager.send_input(session_id, "i")
        time.sleep(1)
        
        # Type some text
        text_to_type = "Hello! This is a demonstration of vim working through the terminal MCP server.\nI can type multiple lines,\nand even add some special characters: @#$%^&*()\nThis is pretty cool! 🎉"
        print(f"⌨️  Typing text: '{text_to_type[:50]}...'")
        terminal_manager.send_input(session_id, text_to_type)
        time.sleep(1)
        
        # Show screen after typing
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"\n📺 SCREEN AFTER TYPING:")
        print("=" * 50)
        print(screen_content)
        print("=" * 50)
        
        # Exit insert mode
        print("\n🚪 Exiting insert mode (pressing Escape)...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape key
        time.sleep(1)
        
        # Show screen after exiting insert mode
        screen_content = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print(f"\n📺 SCREEN AFTER EXITING INSERT MODE:")
        print("=" * 50)
        print(screen_content)
        print("=" * 50)
        
        # Save and quit
        print("\n💾 Saving and quitting (:wq)...")
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(2)
        
        # Check if vim is still running
        _, _, still_running = terminal_manager.get_session_state(session_id)
        print(f"📊 Vim still running after :wq: {still_running}")
        
        # Terminate session if still running
        if still_running:
            terminal_manager.terminate_session(session_id)
    
    # Read and display the saved file content
    print(f"\n📄 READING SAVED FILE: {filename}")
    print("=" * 50)
    try:
        with open(filename, "r") as f:
            content = f.read()
        print(content)
        print("=" * 50)
        print(f"✅ File successfully saved with {len(content)} characters!")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
    
    print("\n🎯 DEMONSTRATION COMPLETE!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
