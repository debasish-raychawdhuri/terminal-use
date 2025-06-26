#!/usr/bin/env python3
"""
Test the final fixed live display.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_final_fixed_live():
    """Test the final fixed live display."""
    print("=== Testing FINAL FIXED Live Display ===\n")
    
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
            title="FINAL FIXED - Live Display",
            update_interval=0.5
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Test shell colors
        print("3. Testing shell colors...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED\\033[0m \\033[32mGREEN\\033[0m \\033[34mBLUE\\033[0m'\n")
        time.sleep(2)
        
        print("4. Shell should show colored text. Now testing vim...")
        
        # Launch vim
        terminal_manager.send_input(session_id, "vim final_test.txt\n")
        time.sleep(4)
        
        print("5. CHECK THE LIVE DISPLAY NOW:")
        print("   ✓ Should show vim interface with tildes (~)")
        print("   ✓ Should NOT show '25h' or other escape sequences")
        print("   ✓ Should show status line at bottom")
        print("   ✓ Should be clean and properly formatted")
        
        # Interact with vim
        print("6. Interacting with vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "This is working!\nVim display is clean!\nNo more garbled text!")
        time.sleep(2)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        
        print("   Should show text in vim and '-- INSERT --' mode indicator")
        
        # Save and quit
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(3)
        
        print("7. Should be back to shell now...")
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32mSUCCESS - Vim worked properly!\\033[0m'\n")
        time.sleep(2)
        
        print("8. FINAL VERIFICATION:")
        print("   ✓ Vim interface was clean (no garbled text)")
        print("   ✓ No escape sequences visible as text")
        print("   ✓ Proper screen clearing and updates")
        print("   ✓ Colors preserved in both shell and vim")
        print("   ✓ Clean transition back to shell")
        
        print("\nIf all the above worked, the terminal emulation is ACTUALLY fixed!")
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
    test_final_fixed_live()
