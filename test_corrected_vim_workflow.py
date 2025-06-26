#!/usr/bin/env python3
"""
Test the corrected vim workflow using actual terminal dimensions.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_corrected_vim_workflow():
    """Test vim workflow with corrected dimension handling."""
    print("=== Testing Corrected Vim Workflow (Using Actual Terminal Dimensions) ===\n")
    
    # Create managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Step 1: Start bash session
        print("Step 1: Starting bash session...")
        session_id = terminal_manager.generate_session_id()
        
        output, exit_code, running = terminal_manager.run_command(
            "bash",
            session_id,
            use_terminal_emulator=True,
            timeout=10
        )
        
        # Check actual terminal dimensions
        if session_id in terminal_manager.sessions:
            session = terminal_manager.sessions[session_id]
            if hasattr(session, 'dimensions'):
                rows, cols = session.dimensions
                print(f"Terminal session created with actual dimensions: {cols}x{rows} (width x height)")
        
        # Step 2: Start live display (should use actual dimensions)
        print("\nStep 2: Starting live display using actual terminal dimensions...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Corrected Bash + Vim Session",
            update_interval=0.2
            # Note: No width/height parameters - uses actual terminal dimensions
        )
        
        print(f"Live display started: {result['display_id']}")
        print("The display window should match the terminal's actual size!")
        
        # Step 3: Verify terminal size
        print("\nStep 3: Verifying terminal size...")
        terminal_manager.send_input(session_id, "echo 'Checking terminal size:'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "echo \"Columns: $(tput cols), Lines: $(tput lines)\"\n")
        time.sleep(2)
        
        # Step 4: Open vim with a file
        print("\nStep 4: Opening vim...")
        terminal_manager.send_input(session_id, "vim corrected_test.txt\n")
        time.sleep(3)
        
        # Step 5: Write content in vim
        print("\nStep 5: Writing content in vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        
        # Write content that tests the full width
        content = [
            "This file tests the corrected live terminal display functionality.",
            "The display should use the terminal's actual dimensions (100x40).",
            "This line is exactly 100 characters long to test width: " + "x" * 37,
            "",
            "Key improvements:",
            "- Uses actual terminal dimensions instead of forced parameters",
            "- Preserves authentic terminal layout and sizing", 
            "- Displays content exactly as it appears in the real terminal",
            "",
            "End of test file."
        ]
        
        for line in content:
            terminal_manager.send_input(session_id, line + "\n")
            time.sleep(0.5)
        
        # Step 6: Save and exit vim
        print("\nStep 6: Saving and exiting vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":wq\n")
        time.sleep(2)
        
        # Step 7: Verify the file
        print("\nStep 7: Verifying the saved file...")
        terminal_manager.send_input(session_id, "echo 'File contents:'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "cat corrected_test.txt\n")
        time.sleep(2)
        
        terminal_manager.send_input(session_id, "echo 'File info:'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "wc -l corrected_test.txt\n")
        time.sleep(1)
        
        # Show final state
        print("\nStep 8: Final verification...")
        session_data = terminal_manager.get_session_output(session_id, raw_output=False)
        if session_data:
            print("Final terminal state:")
            print("=" * 100)
            print(session_data['output'])
            print("=" * 100)
        
        print("\n=== Corrected Workflow Complete! ===")
        print("Key points to verify in the live display:")
        print("- Window size matches terminal's actual dimensions (100x40)")
        print("- All content is displayed without artificial wrapping")
        print("- The 100-character test line displays properly")
        print("- Vim interface appears exactly as it would in a real terminal")
        
        print("\nPress Enter to stop the live display...")
        input()
        
        # Cleanup
        display_id = result["display_id"]
        stop_result = live_manager.stop_display(display_id)
        print(f"Live display stopped: {stop_result}")
        
    except Exception as e:
        print(f"Error during corrected workflow test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("Cleaning up...")
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_corrected_vim_workflow()
