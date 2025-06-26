#!/usr/bin/env python3
"""
Debug script to check if the first line is being displayed correctly.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager
from terminal_mcp_server.ansi_to_text_2d import convert_ansi_to_text_2d
import time

def debug_first_line():
    """Debug the first line display issue."""
    print("Debugging first line display...")
    
    # Create terminal manager
    terminal_manager = TerminalManager()
    
    try:
        # Start a simple bash session
        session_id = terminal_manager.generate_session_id()
        print(f"Starting bash session: {session_id}")
        
        output, exit_code, running = terminal_manager.run_command(
            "bash",
            session_id,
            use_terminal_emulator=True,
            timeout=5
        )
        
        print(f"Initial output: {repr(output)}")
        print(f"Running: {running}")
        
        # Wait a moment for the session to initialize
        time.sleep(1)
        
        # Send a simple command
        print("\nSending 'echo Hello World' command...")
        output, exit_code, running = terminal_manager.send_input(session_id, "echo 'Hello World'\n")
        print(f"After echo command: {repr(output)}")
        
        # Wait for command to execute
        time.sleep(1)
        
        # Get the session output for live display
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            raw_output = session_data['output']
            print(f"\nRaw session output: {repr(raw_output)}")
            
            # Convert to 2D text
            text_2d = convert_ansi_to_text_2d(raw_output, width=80, height=25)
            print(f"\n2D converted text:")
            print("=" * 80)
            print(text_2d)
            print("=" * 80)
            
            # Show line by line
            lines = text_2d.split('\n')
            print(f"\nLine by line analysis ({len(lines)} lines):")
            for i, line in enumerate(lines):
                print(f"Line {i:2d}: {repr(line)}")
        
        # Now test the live display
        print(f"\nTesting live display...")
        live_manager = LiveTerminalManager()
        
        result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Debug First Line",
            update_interval=0.5,
            width=80,
            height=25
        )
        
        print(f"Live display result: {result}")
        
        if result["status"] == "started":
            print("Live display started! Check if the first line is visible.")
            print("Press Enter to send more commands...")
            input()
            
            # Send more commands to test
            print("Sending 'ls -la' command...")
            terminal_manager.send_input(session_id, "ls -la\n")
            
            print("Sending 'pwd' command...")
            time.sleep(2)
            terminal_manager.send_input(session_id, "pwd\n")
            
            print("Commands sent. Check the live display.")
            print("Press Enter to stop...")
            input()
            
            # Stop the display
            display_id = result["display_id"]
            stop_result = live_manager.stop_display(display_id)
            print(f"Stop result: {stop_result}")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("Cleaning up...")
        terminal_manager.cleanup()

if __name__ == "__main__":
    debug_first_line()
