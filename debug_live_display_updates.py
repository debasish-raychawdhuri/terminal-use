#!/usr/bin/env python3
"""
Debug the live display update mechanism specifically.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def debug_live_display_updates():
    """Debug what happens in the live display update loop."""
    print("=== DEBUGGING LIVE DISPLAY UPDATES ===\n")
    
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
        
        # Start live display with very slow updates for debugging
        print("2. Starting live display with slow updates...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Debug Live Updates",
            update_interval=2.0  # Very slow updates
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch console for [DEBUG] messages from live display...")
        
        # Send simple command
        print("3. Sending simple command...")
        terminal_manager.send_input(session_id, "echo 'SHELL COMMAND'\n")
        
        print("Waiting 5 seconds for update...")
        time.sleep(5)
        
        # Check what the live display should be getting
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"Session data length: {len(session_data['output'])}")
            print(f"Last 200 chars: {repr(session_data['output'][-200:])}")
        
        # Launch vim
        print("4. Launching vim...")
        terminal_manager.send_input(session_id, "vim debug_live.txt\n")
        
        print("Waiting 5 seconds for vim to load and display to update...")
        time.sleep(5)
        
        # Check what should be displayed now
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"After vim - session data length: {len(session_data['output'])}")
            print(f"Content sample: {repr(session_data['output'][:200])}")
            
            # Check if this is TUI content
            if session_id in terminal_manager.sessions:
                session = terminal_manager.sessions[session_id]
                is_tui = terminal_manager._is_tui_active(session)
                print(f"TUI detected: {is_tui}")
                
                if is_tui and hasattr(session, 'get_screen_content'):
                    screen_content = session.get_screen_content()
                    print(f"Screen content length: {len(screen_content)}")
                    print(f"Screen content: {repr(screen_content[:200])}")
        
        print("5. Check the live display window:")
        print("   - Does it show the vim interface?")
        print("   - Or does it still show the shell?")
        print("   - Are there any [DEBUG] messages in console?")
        
        print("\nWaiting 10 more seconds for any delayed updates...")
        time.sleep(10)
        
        print("6. If the display didn't update to show vim, the live display update loop is broken.")
        
        print("\nPress Enter to quit vim and continue debugging...")
        input()
        
        # Quit vim
        terminal_manager.send_input(session_id, "\x1b:q!\n")
        time.sleep(5)
        
        print("7. After vim exit - check if display returns to shell")
        
        print("\nPress Enter to stop debugging...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during live display debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    debug_live_display_updates()
