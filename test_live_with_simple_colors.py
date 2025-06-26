#!/usr/bin/env python3
"""
Test the live display with the working simple color system.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_live_with_simple_colors():
    """Test live display with working simple colors."""
    print("=== Testing Live Display with Simple Colors ===\n")
    
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
        print("2. Starting live display with simple colors...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Live Display - Simple Colors Working",
            update_interval=0.5
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch console for [DEBUG] messages...")
        
        # Test colors
        print("3. Testing colors in live display...")
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED TEXT\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGREEN TEXT\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBLUE TEXT\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mBOLD YELLOW\\033[0m'\n")
        time.sleep(2)
        
        # Test colored ls
        terminal_manager.send_input(session_id, "ls --color=always\n")
        time.sleep(2)
        
        print("4. Check the live display window:")
        print("   ✓ Should show RED, GREEN, BLUE, BOLD YELLOW colored text")
        print("   ✓ Should show colored directory listing")
        print("   ✗ Should NOT show escape sequences like \\033[31m")
        
        print("\nPress Enter to test vim (TUI)...")
        input()
        
        # Test vim
        print("5. Testing vim...")
        terminal_manager.send_input(session_id, "vim test_colors.txt\n")
        time.sleep(3)
        
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "Colors work in live display!\nNo more escape sequences!")
        time.sleep(2)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(2)
        
        # Final color test
        terminal_manager.send_input(session_id, "echo -e '\\033[92mSUCCESS - All colors working!\\033[0m'\n")
        time.sleep(2)
        
        print("6. Final check:")
        print("   ✓ Vim should have been clean (no escape sequences)")
        print("   ✓ Final SUCCESS message should be bright green")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during live color test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_live_with_simple_colors()
