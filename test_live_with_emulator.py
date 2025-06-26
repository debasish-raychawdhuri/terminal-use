#!/usr/bin/env python3
"""
Test the live display with proper terminal emulation.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_live_with_emulator():
    """Test live display with proper terminal emulation."""
    print("=== Testing Live Display with Terminal Emulation ===\n")
    
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
        print("2. Starting live display with terminal emulation...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Live Display - Terminal Emulation",
            update_interval=0.5
        )
        
        print(f"Live display started: {result['display_id']}")
        print("Watch console for [DEBUG] messages...")
        
        # Test shell colors
        print("3. Testing shell colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED\\033[0m \\033[32mGREEN\\033[0m \\033[34mBLUE\\033[0m'\n")
        time.sleep(2)
        
        # Test vim
        print("4. Testing vim (should have proper screen management)...")
        terminal_manager.send_input(session_id, "vim test_emulator.txt\n")
        time.sleep(4)
        
        print("5. Vim should now be displayed properly:")
        print("   ✓ Should show clean vim interface")
        print("   ✓ Should preserve vim colors")
        print("   ✓ Should NOT show shell history bleeding through")
        print("   ✓ Should have proper cursor positioning")
        
        # Interact with vim
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "Terminal emulation working!\nProper screen management!\nColors and positioning correct!")
        time.sleep(2)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(3)
        
        print("6. Back to shell...")
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32mVim test completed!\\033[0m'\n")
        time.sleep(2)
        
        # Test calculator
        print("7. Testing calculator (should not be garbled)...")
        terminal_manager.send_input(session_id, "terminal_calculator\n")
        time.sleep(4)
        
        print("8. Calculator should be displayed properly:")
        print("   ✓ Should show calculator interface cleanly")
        print("   ✓ Should preserve calculator colors")
        print("   ✓ Should NOT be scattered or garbled")
        print("   ✓ Should have proper layout")
        
        # Test calculator
        terminal_manager.send_input(session_id, "1")
        time.sleep(1)
        terminal_manager.send_input(session_id, "5")
        time.sleep(1)
        terminal_manager.send_input(session_id, "+")
        time.sleep(1)
        terminal_manager.send_input(session_id, "2")
        time.sleep(1)
        terminal_manager.send_input(session_id, "5")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 15 + 25 = 40")
        
        print("\n9. Verification checklist:")
        print("   ✓ Shell colors work properly")
        print("   ✓ Vim interface is clean and positioned correctly")
        print("   ✓ Calculator interface is not garbled")
        print("   ✓ No content bleeding between applications")
        print("   ✓ Proper screen clearing and positioning")
        
        print("\nPress Enter to quit calculator and finish test...")
        input()
        
        # Quit calculator
        terminal_manager.send_input(session_id, "q")
        time.sleep(2)
        
        # Final test
        terminal_manager.send_input(session_id, "echo -e '\\033[1;34mAll emulation tests completed!\\033[0m'\n")
        time.sleep(2)
        
        print("10. Final check - should be back to clean shell with colors")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during emulation test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_live_with_emulator()
