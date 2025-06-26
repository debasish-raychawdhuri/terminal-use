#!/usr/bin/env python3
"""
Debug color display with detailed logging.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time
import logging

# Enable all logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_debug_colors():
    """Test colors with debug output."""
    print("=== Debug Color Test ===\n")
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Start bash session
        print("1. Starting bash session...")
        session_id = terminal_manager.generate_session_id()
        
        output, exit_code, running = terminal_manager.run_command(
            "bash",
            session_id,
            use_terminal_emulator=True,
            timeout=60
        )
        
        print(f"Session ID: {session_id}")
        
        # Start live display
        print("2. Starting live display...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Debug Color Test",
            update_interval=1.0  # Slow updates for debugging
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch the console output for debug messages...")
        
        # Send a simple color command
        print("3. Sending color command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED\\033[0m'\n")
        
        # Wait for update
        print("Waiting 3 seconds for display update...")
        time.sleep(3)
        
        print("4. Check the live display window:")
        print("   - Should show 'RED' in red color")
        print("   - If you see \\033[31mRED\\033[0m as text, colors aren't working")
        print("   - Check console output above for debug messages")
        
        print("\nPress Enter to continue...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during debug test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_debug_colors()
