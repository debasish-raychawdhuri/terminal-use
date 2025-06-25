#!/usr/bin/env python3
"""
Test terminal_calculator TUI program to compute 43.45*55.6
"""

import sys
import time
from terminal_mcp_server.terminal_manager import TerminalManager

def main():
    """Test terminal_calculator TUI program."""
    print("🧮 TESTING TERMINAL_CALCULATOR TUI PROGRAM")
    print("=" * 60)
    print("Task: Compute 43.45 * 55.6")
    print("Goal: Test terminal simulator by reading TUI interface")
    print()
    
    terminal_manager = TerminalManager()
    session_id = terminal_manager.generate_session_id()
    
    # Start terminal_calculator
    print("🚀 Starting terminal_calculator...")
    output, exit_code, running = terminal_manager.run_command(
        "terminal_calculator", 
        session_id, 
        timeout=30,
        use_terminal_emulator=True,
        terminal_emulator="xterm"
    )
    
    print(f"✅ Calculator started - Running: {running}")
    
    if running:
        # Wait for calculator to initialize
        print("⏳ Waiting for calculator to initialize...")
        time.sleep(2)
        
        # Read initial screen to understand the interface
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("\n📺 INITIAL CALCULATOR SCREEN:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Now I need to understand how to use this calculator
        # Let me try entering the first number: 43.45
        print("\n⌨️  Entering first number: 43.45")
        terminal_manager.send_input(session_id, "43.45")
        time.sleep(1)
        
        # Read screen after entering first number
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("\n📺 SCREEN AFTER ENTERING 43.45:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Enter multiplication operator
        print("\n⌨️  Entering multiplication operator: *")
        terminal_manager.send_input(session_id, "*")
        time.sleep(1)
        
        # Read screen after operator
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("\n📺 SCREEN AFTER ENTERING *:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Enter second number: 55.6
        print("\n⌨️  Entering second number: 55.6")
        terminal_manager.send_input(session_id, "55.6")
        time.sleep(1)
        
        # Read screen after second number
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("\n📺 SCREEN AFTER ENTERING 55.6:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Press Enter to calculate
        print("\n⌨️  Pressing Enter to calculate...")
        terminal_manager.send_input(session_id, "\n")
        time.sleep(1)
        
        # Read final screen with result
        screen = terminal_manager.get_session_state(session_id, raw_output=False)[0]
        print("\n📺 FINAL SCREEN WITH RESULT:")
        print("=" * 50)
        print(screen)
        print("=" * 50)
        
        # Try to extract the result from the screen
        print("\n🔍 ANALYZING SCREEN FOR RESULT:")
        lines = screen.split('\n')
        for i, line in enumerate(lines):
            if '43.45' in line or '55.6' in line or '*' in line:
                print(f"Line {i}: {line}")
        
        # Look for the calculated result
        print("\n🎯 LOOKING FOR CALCULATION RESULT:")
        expected_result = 43.45 * 55.6
        print(f"Expected result: {expected_result}")
        
        for i, line in enumerate(lines):
            # Look for numbers that might be the result
            if any(char.isdigit() for char in line) and '=' in line:
                print(f"Potential result line {i}: {line}")
            elif str(int(expected_result)) in line or f"{expected_result:.2f}" in line:
                print(f"Found expected result in line {i}: {line}")
        
        # Exit calculator
        print("\n🚪 Exiting calculator...")
        terminal_manager.send_input(session_id, "q")  # Try 'q' for quit
        time.sleep(1)
        
        # Check if still running
        _, _, still_running = terminal_manager.get_session_state(session_id)
        if still_running:
            # Try Ctrl+C
            terminal_manager.send_input(session_id, "\x03")
            time.sleep(1)
        
        # Terminate session
        terminal_manager.terminate_session(session_id)
    
    print("\n✅ CALCULATOR TEST COMPLETE!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
