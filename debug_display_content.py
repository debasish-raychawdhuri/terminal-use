#!/usr/bin/env python3
"""
Debug what content is being sent to the live display.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
import time

def debug_display_content():
    """Debug the content being sent to live display."""
    print("=== Debugging Display Content ===\n")
    
    terminal_manager = TerminalManager()
    
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
        
        # Send a colorful command
        print("2. Sending colorful command...")
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED TEXT\\033[0m'\n")
        time.sleep(2)
        
        # Check what the session output looks like
        print("3. Checking session output...")
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            raw_output = session_data['output']
            print(f"Raw output length: {len(raw_output)} characters")
            print(f"Raw output (first 500 chars): {repr(raw_output[:500])}")
            
            # Look for color sequences
            if '\x1b[31m' in raw_output:
                print("✓ Found red color sequence \\x1b[31m")
            else:
                print("✗ No red color sequence found")
            
            if '\x1b[0m' in raw_output:
                print("✓ Found reset sequence \\x1b[0m")
            else:
                print("✗ No reset sequence found")
        
        # Test TUI detection
        print("4. Testing TUI detection...")
        session = terminal_manager.sessions[session_id]
        is_tui = terminal_manager._is_tui_active(session)
        print(f"TUI detected: {is_tui}")
        
        # Open vim
        print("5. Opening vim...")
        terminal_manager.send_input(session_id, "vim debug_test.txt\n")
        time.sleep(3)
        
        # Check TUI detection again
        is_tui_after_vim = terminal_manager._is_tui_active(session)
        print(f"TUI detected after vim: {is_tui_after_vim}")
        
        # Check vim output
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            vim_output = session_data['output']
            print(f"Vim output length: {len(vim_output)} characters")
            
            # Look for problematic sequences
            if '25h' in vim_output:
                print("✗ Found '25h' in output (should be filtered)")
            else:
                print("✓ No '25h' found")
            
            if '\x1b[?1049h' in vim_output:
                print("✓ Found alternative screen buffer sequence (TUI indicator)")
            
            # Show last 200 characters
            print(f"Last 200 chars of vim output: {repr(vim_output[-200:])}")
        
        # Exit vim
        terminal_manager.send_input(session_id, "\x1b:q!\n")
        time.sleep(2)
        
        print("\n=== Debug Summary ===")
        print("Check the output above for:")
        print("- Color sequences (\\x1b[31m, \\x1b[0m)")
        print("- TUI detection working")
        print("- Problematic sequences being filtered")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        terminal_manager.cleanup()

if __name__ == "__main__":
    debug_display_content()
