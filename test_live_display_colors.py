#!/usr/bin/env python3
"""
Test colors specifically in the live display.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def test_live_display_colors():
    """Test colors in live display specifically."""
    print("=== Testing Colors in Live Display ===\n")
    
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
            title="Live Display Color Test",
            update_interval=0.5  # Slower updates for debugging
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Send a simple color command
        print("3. Sending color command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED TEXT TEST\\033[0m'\n")
        
        # Wait and check what the session contains
        time.sleep(2)
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            content = session_data['output']
            print(f"Session content length: {len(content)}")
            
            # Check for color sequences
            if '\x1b[31m' in content:
                print("✓ Red color sequence found in session data")
            else:
                print("✗ No red color sequence in session data")
            
            # Show a sample of the content
            print(f"Content sample: {repr(content[-200:])}")
        
        print("\n4. The live display should now show RED TEXT.")
        print("If you don't see red text, there's an issue with the live display color rendering.")
        
        # Send more colors
        print("5. Sending more colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGREEN\\033[0m and \\033[34mBLUE\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mBOLD YELLOW\\033[0m'\n")
        time.sleep(2)
        
        print("6. You should now see GREEN, BLUE, and BOLD YELLOW text in the live display.")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during live display color test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_live_display_colors()
