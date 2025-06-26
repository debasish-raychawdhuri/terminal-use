#!/usr/bin/env python3
"""
Demo script showing how to use the live terminal display with various commands.
"""

import time
from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def demo_live_terminal():
    """Demonstrate live terminal display with various commands."""
    print("=== Live Terminal Display Demo ===\n")
    
    # Create managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Demo 1: Basic colorful output
        print("Demo 1: Basic colorful output")
        session_id1 = terminal_manager.generate_session_id()
        
        terminal_manager.run_command(
            "echo -e '\\033[31m█\\033[32m█\\033[33m█\\033[34m█\\033[35m█\\033[36m█\\033[0m Rainbow!'; "
            "echo 'This is a live terminal display demo'; "
            "echo 'The window updates every 200ms'; "
            "for i in {1..10}; do echo \"Line $i - $(date)\"; sleep 1; done",
            session_id1,
            use_terminal_emulator=True
        )
        
        result1 = live_manager.show_session_live(
            session_id=session_id1,
            terminal_manager=terminal_manager,
            title="Demo 1: Colorful Output",
            update_interval=0.2
        )
        print(f"Started display: {result1['display_id']}")
        
        # Demo 2: Directory listing with colors
        print("\nDemo 2: Directory listing")
        session_id2 = terminal_manager.generate_session_id()
        
        terminal_manager.run_command(
            "ls --color=always -la /; echo ''; echo 'Directory listing complete'",
            session_id2,
            use_terminal_emulator=True
        )
        
        result2 = live_manager.show_session_live(
            session_id=session_id2,
            terminal_manager=terminal_manager,
            title="Demo 2: Directory Listing",
            update_interval=0.3,
            width=120,
            height=30
        )
        print(f"Started display: {result2['display_id']}")
        
        # Demo 3: Interactive-style output
        print("\nDemo 3: Simulated interactive output")
        session_id3 = terminal_manager.generate_session_id()
        
        terminal_manager.run_command(
            "echo 'Simulating interactive application...'; "
            "for i in {1..20}; do "
            "  echo -ne '\\rProgress: ['$(printf '%*s' $((i*2)) '' | tr ' ' '=')$(printf '%*s' $((40-i*2)) '' | tr ' ' ' ')'] '$i'/20'; "
            "  sleep 0.5; "
            "done; "
            "echo ''; echo 'Complete!'",
            session_id3,
            use_terminal_emulator=True
        )
        
        result3 = live_manager.show_session_live(
            session_id=session_id3,
            terminal_manager=terminal_manager,
            title="Demo 3: Progress Bar",
            update_interval=0.1,
            width=80,
            height=20
        )
        print(f"Started display: {result3['display_id']}")
        
        # Show all active displays
        print("\n=== Active Displays ===")
        displays = live_manager.list_displays()
        for display in displays["displays"]:
            print(f"- {display['title']} (ID: {display['display_id'][:8]}...)")
            print(f"  Session: {display['session_id'][:8]}...")
            print(f"  Update: {display['update_interval']}s")
            print(f"  Running: {display['is_running']}")
            print()
        
        print("All terminal windows should now be visible and updating live!")
        print("Press Enter to stop all displays...")
        input()
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("Stopping all displays and cleaning up...")
        live_manager.cleanup()
        terminal_manager.cleanup()
        print("Demo complete!")

if __name__ == "__main__":
    demo_live_terminal()
