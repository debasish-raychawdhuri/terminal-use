#!/usr/bin/env python3
"""
Simple debug test to see what's happening with colors.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_debug_simple():
    """Simple debug test."""
    print("=== Simple Debug Test ===\n")
    
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
            title="Debug Test",
            update_interval=2.0  # Very slow updates
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch console output for [DEBUG] messages...")
        
        # Send one simple color command
        print("3. Sending simple color command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED\\033[0m'\n")
        
        # Wait for update
        print("Waiting 5 seconds for display update...")
        time.sleep(5)
        
        print("4. Check console output above for debug messages")
        print("5. Check live display - should show 'RED' in red color")
        
        print("\nPress Enter to stop...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_debug_simple()
