#!/usr/bin/env python3
"""
Final test of live display with colors and escape sequence filtering.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_final_live_display():
    """Final test of the live display with all fixes."""
    print("=== Final Live Display Test ===\n")
    
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
            title="Final Test - Colors and Clean Display",
            update_interval=0.3
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Test 1: Colors
        print("3. Testing colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED\\033[0m \\033[32mGREEN\\033[0m \\033[34mBLUE\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mBOLD YELLOW\\033[0m \\033[35mMAGENTA\\033[0m'\n")
        time.sleep(2)
        
        # Test 2: Colored ls
        print("4. Testing colored directory listing...")
        terminal_manager.send_input(session_id, "ls --color=always\n")
        time.sleep(2)
        
        # Test 3: TUI application (vim)
        print("5. Testing TUI application (vim)...")
        terminal_manager.send_input(session_id, "vim final_test.txt\n")
        time.sleep(3)
        
        # Interact with vim
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "Colors work!\nNo escape sequences visible!\nTUI display is clean!")
        time.sleep(2)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(2)
        
        # Test 4: Back to colored shell
        print("6. Back to colored shell...")
        terminal_manager.send_input(session_id, "echo -e '\\033[92mBRIGHT GREEN - All tests complete!\\033[0m'\n")
        time.sleep(1)
        
        print("\n=== Final Verification ===")
        print("Check the live display window for:")
        print("✓ RED, GREEN, BLUE, BOLD YELLOW, MAGENTA colored text")
        print("✓ Colored directory listing (ls --color)")
        print("✓ Clean vim interface (no escape sequences visible)")
        print("✓ BRIGHT GREEN final message")
        print("✗ NO literal escape sequences like \\033[31m or \\x1b]697")
        
        print("\nIf you see colors and no escape sequences, the fixes are working!")
        print("Press Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during final test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_final_live_display()
