#!/usr/bin/env python3
"""
Test terminal_calculator with the fixed escape sequence handling.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_calculator_fixed():
    """Test calculator with fixed escape handling."""
    print("=== Testing Calculator with Fixed Escape Handling ===\n")
    
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
        print("2. Starting live display with improved filtering...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Calculator - Fixed Escape Handling",
            update_interval=0.5
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Test shell colors first
        print("3. Testing shell colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[32mLaunching calculator...\\033[0m'\n")
        time.sleep(2)
        
        # Launch calculator
        print("4. Launching terminal_calculator...")
        terminal_manager.send_input(session_id, "terminal_calculator\n")
        time.sleep(4)  # Give it time to fully load
        
        print("5. Calculator should now be displayed cleanly!")
        print("   Check the live display:")
        print("   ✓ Should show calculator interface (not escape sequences)")
        print("   ✓ Should be readable and clean")
        print("   ✓ No 'infinite train' of escape sequences")
        
        # Test some calculations
        print("6. Testing calculator operations...")
        
        # Simple calculation
        terminal_manager.send_input(session_id, "1")
        time.sleep(1)
        terminal_manager.send_input(session_id, "2")
        time.sleep(1)
        terminal_manager.send_input(session_id, "+")
        time.sleep(1)
        terminal_manager.send_input(session_id, "3")
        time.sleep(1)
        terminal_manager.send_input(session_id, "4")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 12 + 34 = 46")
        
        # Clear and another calculation
        terminal_manager.send_input(session_id, "c")  # Clear
        time.sleep(1)
        terminal_manager.send_input(session_id, "9")
        time.sleep(1)
        terminal_manager.send_input(session_id, "*")
        time.sleep(1)
        terminal_manager.send_input(session_id, "8")
        time.sleep(1)
        terminal_manager.send_input(session_id, "=")
        time.sleep(2)
        
        print("   Calculator should show: 9 * 8 = 72")
        
        print("7. Verification checklist:")
        print("   ✓ Calculator display is clean and readable")
        print("   ✓ No escape sequences visible as text")
        print("   ✓ Calculations work and display properly")
        print("   ✓ Live display updates smoothly without spam")
        
        print("\nPress Enter to quit calculator...")
        input()
        
        # Quit calculator
        print("8. Quitting calculator...")
        terminal_manager.send_input(session_id, "q")
        time.sleep(2)
        
        # Back to shell
        print("9. Back to shell...")
        terminal_manager.send_input(session_id, "echo -e '\\033[1;34mCalculator test completed!\\033[0m'\n")
        time.sleep(2)
        
        print("10. Final check:")
        print("    ✓ Should be back to colored shell")
        print("    ✓ Success message should be bold blue")
        print("    ✓ Transition should be clean")
        
        print("\nPress Enter to stop the test...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error during calculator test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_calculator_fixed()
