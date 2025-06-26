#!/usr/bin/env python3
"""
Test that live display uses actual terminal dimensions instead of forced ones.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_actual_dimensions():
    """Test that live display respects actual terminal dimensions."""
    print("=== Testing Actual Terminal Dimensions ===\n")
    
    # Create managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Create a terminal session with specific dimensions
        print("Step 1: Creating terminal session with 80x25 dimensions...")
        session_id = terminal_manager.generate_session_id()
        
        # Start bash with terminal emulator (which sets dimensions to 40x100 by default)
        output, exit_code, running = terminal_manager.run_command(
            "bash",
            session_id,
            use_terminal_emulator=True,
            timeout=10
        )
        
        print(f"Session created: {session_id}")
        
        # Check the actual dimensions of the session
        if session_id in terminal_manager.sessions:
            session = terminal_manager.sessions[session_id]
            if hasattr(session, 'dimensions'):
                rows, cols = session.dimensions
                print(f"Actual terminal dimensions: {cols}x{rows} (width x height)")
            else:
                print("Session doesn't have dimensions attribute")
        
        # Step 2: Create live display that should use actual dimensions
        print("\nStep 2: Creating live display (should use actual terminal dimensions)...")
        
        # Pass different dimensions to see if they're ignored
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Actual Dimensions Test",
            update_interval=0.3,
            width=50,   # This should be ignored
            height=15   # This should be ignored
        )
        
        print(f"Live display started: {result['display_id']}")
        print("The display should use the terminal's actual dimensions (100x40), not the passed ones (50x15)")
        
        # Step 3: Test with some content
        print("\nStep 3: Adding content to see dimension handling...")
        
        # Send a command that shows terminal size
        terminal_manager.send_input(session_id, "echo 'Terminal size test:'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "tput cols; tput lines\n")
        time.sleep(1)
        
        # Send a command that creates wide output
        terminal_manager.send_input(session_id, "echo 'This is a long line to test width handling: " + "x" * 80 + "'\n")
        time.sleep(1)
        
        # Show current session state
        session_data = terminal_manager.get_session_output(session_id, raw_output=False)
        if session_data:
            print("Current terminal content:")
            print("-" * 100)
            print(session_data['output'])
            print("-" * 100)
        
        print("\nStep 4: Verification complete!")
        print("Check the live display window:")
        print("- It should show the full width of the terminal (100 characters)")
        print("- It should show the full height of the terminal (40 lines)")
        print("- The long line should be displayed properly without artificial wrapping")
        
        print("\nPress Enter to stop the live display...")
        input()
        
        # Cleanup
        display_id = result["display_id"]
        stop_result = live_manager.stop_display(display_id)
        print(f"Live display stopped: {stop_result}")
        
    except Exception as e:
        print(f"Error during dimension test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("Cleaning up...")
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_actual_dimensions()
