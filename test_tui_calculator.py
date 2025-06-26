#!/usr/bin/env python3
"""
Test TUI application (terminal_calculator) with the live display.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_tui_calculator():
    """Test TUI application with live display."""
    print("=== Testing TUI Application (terminal_calculator) ===\n")
    
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
            title="TUI Calculator Test",
            update_interval=0.3
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # First, test some colors in regular shell
        print("3. Testing colors in shell first...")
        terminal_manager.send_input(session_id, "echo -e '\\033[32mStarting TUI test...\\033[0m'\n")
        time.sleep(2)
        
        # Launch terminal calculator
        print("4. Launching terminal_calculator...")
        terminal_manager.send_input(session_id, "terminal_calculator\n")
        time.sleep(3)
        
        print("5. Calculator should now be running in the live display!")
        print("   Check the live display window:")
        print("   ✓ Should show calculator interface (not shell history)")
        print("   ✓ Should be clean without escape sequences")
        print("   ✓ Should show proper TUI layout")
        
        # Interact with calculator
        print("6. Interacting with calculator...")
        print("   Sending some calculations...")
        
        # Send some keystrokes to the calculator
        terminal_manager.send_input(session_id, "5")
        time.sleep(1)
        terminal_manager.send_input(session_id, "+")
        time.sleep(1)
        terminal_manager.send_input(session_id, "3")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 5 + 3 = 8")
        
        # Another calculation
        terminal_manager.send_input(session_id, "c")  # Clear
        time.sleep(1)
        terminal_manager.send_input(session_id, "1")
        time.sleep(1)
        terminal_manager.send_input(session_id, "0")
        time.sleep(1)
        terminal_manager.send_input(session_id, "*")
        time.sleep(1)
        terminal_manager.send_input(session_id, "7")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 10 * 7 = 70")
        
        print("7. Check TUI display quality:")
        print("   ✓ Calculator interface should be clean and properly formatted")
        print("   ✓ No escape sequences should be visible")
        print("   ✓ Display should update in real-time with calculations")
        print("   ✓ Should show current screen state, not accumulated history")
        
        print("\nPress Enter to quit calculator and return to shell...")
        input()
        
        # Quit calculator
        print("8. Quitting calculator...")
        terminal_manager.send_input(session_id, "q")  # Quit
        time.sleep(2)
        
        # Back to shell - test colors again
        print("9. Back to shell - testing colors again...")
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBack to shell!\\033[0m'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32mTUI test completed successfully!\\033[0m'\n")
        time.sleep(2)
        
        print("10. Final verification:")
        print("    ✓ Should be back to colored shell prompt")
        print("    ✓ Should show 'Back to shell!' in blue")
        print("    ✓ Should show success message in bold green")
        print("    ✓ Transition from TUI to shell should be clean")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during TUI calculator test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_tui_calculator()
