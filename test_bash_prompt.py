#!/usr/bin/env python3
"""
Test specifically for bash prompt visibility.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
import time

def test_bash_prompt():
    """Test bash prompt visibility specifically."""
    print("=== Testing Bash Prompt Visibility ===\n")
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # Start a bash session that stays alive
        print("1. Starting persistent bash session...")
        session_id = terminal_manager.generate_session_id()
        
        output, exit_code, running = terminal_manager.run_command(
            "bash",  # Just bash, no command
            session_id,
            use_terminal_emulator=True,
            timeout=30  # Longer timeout
        )
        
        print(f"Session ID: {session_id}")
        print(f"Initial output: {repr(output)}")
        print(f"Running: {running}")
        
        # Wait for bash to fully initialize
        time.sleep(2)
        
        # Check what we have so far
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"\nRaw output after initialization:")
            print(f"Length: {len(session_data['output'])} characters")
            print(f"Content: {repr(session_data['output'][:500])}...")
        
        # Start live display
        print(f"\n2. Starting live display...")
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Bash Prompt Test",
            update_interval=0.3
        )
        
        print(f"Live display started: {result['display_id']}")
        
        # Send a simple command
        print(f"\n3. Sending 'pwd' command...")
        terminal_manager.send_input(session_id, "pwd\n")
        
        time.sleep(2)
        
        # Check output again
        session_data = terminal_manager.get_session_output(session_id, raw_output=False)
        if session_data:
            print(f"\nOutput after 'pwd' command:")
            lines = session_data['output'].split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"Line {i:2d}: {repr(line)}")
        
        # Send another command
        print(f"\n4. Sending 'echo Hello' command...")
        terminal_manager.send_input(session_id, "echo 'Hello World'\n")
        
        time.sleep(2)
        
        # Final check
        session_data = terminal_manager.get_session_output(session_id, raw_output=False)
        if session_data:
            print(f"\nFinal output:")
            lines = session_data['output'].split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"Line {i:2d}: {repr(line)}")
        
        print(f"\n=== Key Question ===")
        print(f"Do you see any bash prompt lines like:")
        print(f"'(base) debasish@DebasishC-UB:~/work/talentica/terminal-mcp-server$'")
        print(f"in the output above?")
        
        print(f"\nPress Enter to stop live display...")
        input()
        
        # Stop display
        live_manager.stop_display(result["display_id"])
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        live_manager.cleanup()
        terminal_manager.cleanup()

if __name__ == "__main__":
    test_bash_prompt()
