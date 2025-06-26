#!/usr/bin/env python3
"""
Test script for the live terminal display functionality.
"""

import sys
import time
import threading
from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_live_display():
    """Test the live terminal display functionality."""
    print("Testing live terminal display...")
    
    # Create managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Start a terminal session with a colorful command
        session_id = terminal_manager.generate_session_id()
        print(f"Starting terminal session: {session_id}")
        
        # Run a command that produces colorful output
        output, exit_code, running = terminal_manager.run_command(
            "echo -e '\\033[31mRed\\033[0m \\033[32mGreen\\033[0m \\033[34mBlue\\033[0m'; sleep 2; echo 'More output'; ls --color=always",
            session_id,
            timeout=10,
            use_terminal_emulator=True
        )
        
        print(f"Command output: {output[:200]}...")
        print(f"Exit code: {exit_code}, Running: {running}")
        
        # Show the live display
        print("Starting live display...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Test Live Terminal",
            update_interval=0.5,
            width=80,
            height=25
        )
        
        print(f"Live display result: {result}")
        
        if result["status"] == "started":
            print("Live display started successfully!")
            print("The terminal window should now be visible.")
            print("Press Enter to continue...")
            input()
            
            # List displays
            displays = live_manager.list_displays()
            print(f"Active displays: {displays}")
            
            # Stop the display
            if displays["count"] > 0:
                display_id = displays["displays"][0]["display_id"]
                stop_result = live_manager.stop_display(display_id)
                print(f"Stop result: {stop_result}")
        else:
            print(f"Failed to start live display: {result}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("Cleaning up...")
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_live_display()
