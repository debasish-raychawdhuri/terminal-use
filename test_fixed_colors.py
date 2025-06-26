#!/usr/bin/env python3
"""
Test if the color fix works now.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_fixed_colors():
    """Test if colors work now with the TUI detection fix."""
    
    print("=== Testing Fixed Colors ===")
    print("This should now show colors in the live display!")
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
            title="Fixed Colors Test",
            update_interval=0.5
        )
        display_id = display_result['display_id']
        time.sleep(1)
        
        # Test colors
        print("3. Testing colors...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mThis should be RED\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mThis should be GREEN\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mThis should be BLUE\\033[0m'\n")
        time.sleep(1)
        
        # Test TUI detection
        session = terminal_manager.sessions[session_id]
        is_tui = terminal_manager._is_tui_active(session)
        print(f"TUI detected: {is_tui} (should be False for shell)")
        
        # Test raw output
        raw_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if raw_data:
            raw_content = raw_data['output']
            actual_escapes = raw_content.count('\x1b')
            print(f"ANSI sequences in output: {actual_escapes}")
        
        print("\n4. CHECK THE LIVE DISPLAY:")
        print("   You should now see:")
        print("   - RED colored text")
        print("   - GREEN colored text")
        print("   - BLUE colored text")
        print("   - NO escape sequences visible as text")
        print()
        
        colors_visible = input("Can you see the colored text? (y/n): ").lower().strip()
        
        if colors_visible == 'y':
            print("\n🎉 SUCCESS: Colors are now working!")
        else:
            print("\n❌ Still not working. Need more investigation.")
        
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
    test_fixed_colors()
