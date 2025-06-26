#!/usr/bin/env python3
"""
Test TUI applications and color support in live display.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_tui_and_colors():
    """Test TUI applications and color support."""
    print("=== Testing TUI Applications and Colors ===\n")
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Step 1: Start interactive bash session
        print("1. Starting interactive bash session...")
        session_id = terminal_manager.generate_session_id()
        
        output, exit_code, running = terminal_manager.run_command(
            "bash",
            session_id,
            use_terminal_emulator=True,
            timeout=60
        )
        
        print(f"Session ID: {session_id}")
        
        # Step 2: Start live display
        print("2. Starting live display...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="TUI and Colors Test",
            update_interval=0.2
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Step 3: Test colors first
        print("3. Testing colors...")
        print("   Sending colorful commands...")
        
        # Send colorful commands
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRed Text\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGreen Text\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBlue Text\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mBold Yellow\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "ls --color=always\n")
        time.sleep(2)
        
        print("   Colors should now be visible in the live display!")
        
        # Step 4: Test TUI application
        print("4. Testing TUI application (vim)...")
        print("   Opening vim...")
        
        terminal_manager.send_input(session_id, "vim test_tui_colors.txt\n")
        time.sleep(3)
        
        print("   Vim should now be open in the live display!")
        print("   The display should show the vim interface, not accumulated history.")
        
        # Step 5: Interact with vim
        print("5. Interacting with vim...")
        
        # Enter insert mode
        terminal_manager.send_input(session_id, "i")
        time.sleep(1)
        
        # Type some text
        terminal_manager.send_input(session_id, "This is a test of TUI display.\nColors and vim interface should work properly.\nLine 3 of the test.")
        time.sleep(2)
        
        # Exit insert mode
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        
        # Save and quit
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(2)
        
        print("   Vim should have closed and returned to bash prompt.")
        
        # Step 6: Verify we're back to shell
        print("6. Back to shell - testing colors again...")
        
        terminal_manager.send_input(session_id, "echo -e '\\033[35mMagenta - Back to Shell!\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "cat test_tui_colors.txt\n")
        time.sleep(1)
        
        print("\n=== Test Complete ===")
        print("Check the live display window for:")
        print("1. ✓ Colorful text (red, green, blue, yellow, magenta)")
        print("2. ✓ Colored ls output")
        print("3. ✓ Vim interface (not accumulated history)")
        print("4. ✓ Proper TUI screen clearing")
        print("5. ✓ Return to shell with colors")
        
        print("\nPress Enter to stop the live display...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during TUI and color test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_tui_and_colors()
