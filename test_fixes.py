#!/usr/bin/env python3
"""
Test the fixes for colors and TUI screen clearing.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_fixes():
    """Test the color and TUI fixes."""
    print("=== Testing Color and TUI Fixes ===\n")
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Step 1: Start bash session
        print("1. Starting bash session...")
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
            title="Color and TUI Fixes Test",
            update_interval=0.3
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Step 3: Test colors
        print("3. Testing colors...")
        
        # Simple color test
        terminal_manager.send_input(session_id, "echo -e 'Testing colors:'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mThis should be RED\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[32mThis should be GREEN\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[34mThis should be BLUE\\033[0m'\n")
        time.sleep(1)
        
        print("   Check live display: Do you see RED, GREEN, and BLUE colored text?")
        
        # Step 4: Test vim (TUI)
        print("4. Testing vim (TUI application)...")
        print("   Opening vim...")
        
        terminal_manager.send_input(session_id, "vim test_fixes.txt\n")
        time.sleep(3)
        
        print("   Check live display:")
        print("   - Should show vim interface (not bash history)")
        print("   - Should NOT see escape sequences like '25h' or '?1049h'")
        print("   - Should see clean vim interface")
        
        # Interact with vim
        print("5. Interacting with vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "Testing TUI fixes\nColors should work\nNo escape sequences visible")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(2)
        
        print("   Vim should have closed cleanly")
        
        # Step 6: Back to shell with colors
        print("6. Back to shell - final color test...")
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mBOLD YELLOW - Back to shell!\\033[0m'\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "ls --color=always\n")
        time.sleep(2)
        
        print("\n=== Fix Verification ===")
        print("Please check the live display window:")
        print("✓ Colors: RED, GREEN, BLUE, BOLD YELLOW text should be colored")
        print("✓ TUI: Vim interface should be clean (no escape sequences visible)")
        print("✓ Transitions: Clean switch between shell and vim")
        print("✓ ls colors: Directory listing should show colors")
        
        print("\nPress Enter when you've verified the fixes...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during fix test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_fixes()
