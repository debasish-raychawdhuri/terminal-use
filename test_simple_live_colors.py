#!/usr/bin/env python3
"""
Simple test to verify live display colors work.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_simple_live_colors():
    """Simple test for live display colors."""
    
    print("=== SIMPLE LIVE DISPLAY COLOR TEST ===")
    print("This will test ONLY colors, not vim functionality.")
    print()
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    session_id = None
    display_id = None
    
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
        
        # Start live display
        print("2. Starting live display...")
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Simple Color Test",
            update_interval=0.5
        )
        display_id = display_result['display_id']
        time.sleep(1)
        
        # Clear and add simple colored text
        print("3. Adding simple colored text...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mThis should be RED\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mThis should be GREEN\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mThis should be BLUE\\033[0m'\n")
        time.sleep(1)
        
        print("\n4. CHECK THE LIVE DISPLAY:")
        print("   You should see three lines:")
        print("   - 'This should be RED' in red color")
        print("   - 'This should be GREEN' in green color")
        print("   - 'This should be BLUE' in blue color")
        print()
        
        colors_visible = input("Can you see the RED, GREEN, and BLUE colored text? (y/n): ").lower().strip()
        
        if colors_visible == 'y':
            print("\n✅ SUCCESS: Colors are working in live display!")
            print("   The terminal emulation color fix is working correctly.")
        else:
            print("\n❌ FAILURE: Colors are not visible in live display.")
            print("   There's still an issue with color rendering.")
        
    finally:
        print("\nCleaning up...")
        try:
            if display_id:
                live_manager.stop_live_display(display_id)
            live_manager.cleanup()
            if session_id:
                terminal_manager.terminate_session(session_id)
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    test_simple_live_colors()
