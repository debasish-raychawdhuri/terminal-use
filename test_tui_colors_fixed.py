#!/usr/bin/env python3
"""
Test TUI applications with colors preserved and proper screen refresh.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_tui_colors_fixed():
    """Test TUI with colors preserved and proper screen management."""
    print("=== Testing TUI with Colors Preserved ===\n")
    
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
            title="TUI Colors and Screen Refresh Test",
            update_interval=0.5
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch console for [DEBUG] messages about TUI state changes...")
        
        # Test shell colors first
        print("3. Testing shell colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mShell: RED\\033[0m \\033[32mGREEN\\033[0m \\033[34mBLUE\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33mShell: BOLD YELLOW\\033[0m'\n")
        time.sleep(2)
        
        # Launch vim (TUI with colors)
        print("4. Launching vim (TUI with colors)...")
        terminal_manager.send_input(session_id, "vim test_tui_colors.txt\n")
        time.sleep(4)
        
        print("5. Vim should now be displayed:")
        print("   ✓ Should show vim interface (not shell history)")
        print("   ✓ Should preserve vim's colors (if any)")
        print("   ✓ Should be clean without positioning escape sequences")
        print("   ✓ No shell content should bleed through")
        
        # Interact with vim
        print("6. Interacting with vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "Testing TUI colors:\nVim should preserve its interface colors\nNo shell content should show through")
        time.sleep(2)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(3)
        
        print("7. Back to shell - should transition cleanly...")
        terminal_manager.send_input(session_id, "echo -e '\\033[35mBack to shell: MAGENTA\\033[0m'\n")
        time.sleep(2)
        
        # Now test calculator
        print("8. Testing calculator (another TUI)...")
        terminal_manager.send_input(session_id, "echo -e '\\033[36mLaunching calculator...\\033[0m'\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "terminal_calculator\n")
        time.sleep(4)
        
        print("9. Calculator should be displayed:")
        print("   ✓ Should show calculator interface cleanly")
        print("   ✓ Should preserve calculator's colors (if any)")
        print("   ✓ Should NOT show shell history")
        print("   ✓ Should NOT show escape sequence spam")
        
        # Test calculator
        terminal_manager.send_input(session_id, "5")
        time.sleep(1)
        terminal_manager.send_input(session_id, "+")
        time.sleep(1)
        terminal_manager.send_input(session_id, "7")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 5 + 7 = 12")
        
        print("\n10. Check debug output above for TUI state changes")
        print("    Should see: Shell mode -> TUI mode -> Shell mode -> TUI mode")
        
        print("\nPress Enter to quit calculator and finish test...")
        input()
        
        # Quit calculator
        terminal_manager.send_input(session_id, "q")
        time.sleep(2)
        
        # Final shell test
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32mAll TUI tests completed successfully!\\033[0m'\n")
        time.sleep(2)
        
        print("11. Final verification:")
        print("    ✓ Should be back to shell with colors")
        print("    ✓ Success message should be bold green")
        print("    ✓ All transitions should have been clean")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during TUI color test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_tui_colors_fixed()
