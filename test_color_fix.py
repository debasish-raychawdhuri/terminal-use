#!/usr/bin/env python3
"""
Test the color fix - ensuring text widget state is correct.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_color_fix():
    """Test if the color fix works."""
    
    print("=== TESTING COLOR FIX ===")
    print("This tests the fix for text widget state issues.")
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
            title="Color Fix Test",
            update_interval=0.5
        )
        display_id = display_result['display_id']
        time.sleep(1)
        
        # Test colors with the fix
        print("3. Testing colors with fix...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mThis should be RED\\033[0m'\n")
        time.sleep(2)  # Give more time for processing
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mThis should be GREEN\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mThis should be BLUE\\033[0m'\n")
        time.sleep(2)
        
        print("\n4. CHECK THE LIVE DISPLAY:")
        print("   With the fix, you should now see:")
        print("   - 'This should be RED' in RED color")
        print("   - 'This should be GREEN' in GREEN color")
        print("   - 'This should be BLUE' in BLUE color")
        print()
        
        colors_work = input("Do you see the colored text now? (y/n): ").lower().strip()
        
        if colors_work == 'y':
            print("\n🎉 SUCCESS: The color fix is working!")
            print("   Colors are now displaying correctly in live terminal.")
        else:
            print("\n❌ STILL NOT WORKING: Need to investigate further.")
            print("   The text widget state fix didn't resolve the issue.")
        
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
    test_color_fix()
