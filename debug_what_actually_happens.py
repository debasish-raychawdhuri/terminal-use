#!/usr/bin/env python3
"""
Actually debug what's happening instead of assuming things work.
"""

from terminal_mcp_server.terminal_manager import TerminalManager
import time

def debug_actual_behavior():
    """Debug what actually happens when we run vim."""
    print("=== ACTUAL DEBUGGING - No Assumptions ===\n")
    
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
        print(f"Initial output length: {len(output)}")
        print(f"Initial output sample: {repr(output[:200])}")
        
        # Check what we get from the session
        print("\n2. Checking session state...")
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"Session output length: {len(session_data['output'])}")
            print(f"Session running: {session_data['running']}")
            print(f"Last 200 chars: {repr(session_data['output'][-200:])}")
        
        # Send a simple command first
        print("\n3. Sending simple echo command...")
        terminal_manager.send_input(session_id, "echo 'BEFORE VIM'\n")
        time.sleep(2)
        
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"After echo - output length: {len(session_data['output'])}")
            print(f"Last 300 chars: {repr(session_data['output'][-300:])}")
        
        # Now launch vim
        print("\n4. Launching vim...")
        terminal_manager.send_input(session_id, "vim debug_test.txt\n")
        
        # Check what happens immediately
        time.sleep(1)
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"1 sec after vim - output length: {len(session_data['output'])}")
            print(f"Contains alternative screen: {'1049h' in session_data['output']}")
            print(f"Last 500 chars: {repr(session_data['output'][-500:])}")
        
        # Wait longer
        time.sleep(3)
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"4 sec after vim - output length: {len(session_data['output'])}")
            print(f"Last 500 chars: {repr(session_data['output'][-500:])}")
        
        # Check TUI detection
        print("\n5. Checking TUI detection...")
        if session_id in terminal_manager.sessions:
            session = terminal_manager.sessions[session_id]
            is_tui = terminal_manager._is_tui_active(session)
            print(f"TUI detected: {is_tui}")
            
            # Check screen content vs full output
            if hasattr(session, 'get_screen_content'):
                screen_content = session.get_screen_content()
                print(f"Screen content length: {len(screen_content)}")
                print(f"Screen content sample: {repr(screen_content[:300])}")
            
            if hasattr(session, 'get_output'):
                full_output = session.get_output(raw=True)
                print(f"Full output length: {len(full_output)}")
                print(f"Full output != screen content: {full_output != screen_content}")
        
        # Try to interact with vim
        print("\n6. Trying to interact with vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(1)
        terminal_manager.send_input(session_id, "test text")
        time.sleep(1)
        
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"After vim interaction - output length: {len(session_data['output'])}")
            print(f"Last 300 chars: {repr(session_data['output'][-300:])}")
        
        # Try to exit vim
        print("\n7. Trying to exit vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(1)
        terminal_manager.send_input(session_id, ":q!\n")  # Quit without saving
        time.sleep(3)
        
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"After vim exit - output length: {len(session_data['output'])}")
            print(f"Contains exit alt screen: {'1049l' in session_data['output']}")
            print(f"Last 500 chars: {repr(session_data['output'][-500:])}")
        
        # Check if we're back to shell
        print("\n8. Checking if back to shell...")
        terminal_manager.send_input(session_id, "echo 'AFTER VIM'\n")
        time.sleep(2)
        
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        if session_data:
            print(f"After final echo - output length: {len(session_data['output'])}")
            print(f"Last 300 chars: {repr(session_data['output'][-300:])}")
        
        print("\n=== ANALYSIS ===")
        print("Look at the debug output above to understand:")
        print("1. Is vim actually starting? (look for alternative screen sequences)")
        print("2. Is the session getting vim's output? (check output changes)")
        print("3. Is TUI detection working?")
        print("4. Is screen content different from full output?")
        print("5. Does vim exit properly?")
        
    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        terminal_manager.cleanup()

if __name__ == "__main__":
    debug_actual_behavior()
