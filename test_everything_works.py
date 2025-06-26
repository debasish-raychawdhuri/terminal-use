#!/usr/bin/env python3
"""
Test that everything works - colors and terminal_calculator.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_everything_works():
    """Test both colors and terminal_calculator functionality."""
    
    print("=== TESTING EVERYTHING WORKS ===")
    print("This will test:")
    print("1. Basic colors in live display")
    print("2. Terminal calculator functionality")
    print("3. Vim screen clearing (if time permits)")
    print()
    
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    session_id = None
    display_id = None
    
    try:
        # Test 1: Basic colors
        print("=== TEST 1: BASIC COLORS ===")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        time.sleep(1)
        
        # Start live display
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Test Everything - Colors",
            update_interval=0.5
        )
        display_id = display_result['display_id']
        time.sleep(1)
        
        # Test colors
        print("Testing colors...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(1)
        
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRED TEXT\\033[0m'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGREEN TEXT\\033[0m'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBLUE TEXT\\033[0m'\n")
        time.sleep(1)
        
        colors_work = input("\nDo you see RED, GREEN, and BLUE colored text? (y/n): ").lower().strip()
        
        # Clean up first test
        live_manager.stop_display(display_id)
        terminal_manager.terminate_session(session_id)
        time.sleep(1)
        
        # Test 2: Terminal Calculator
        print("\n=== TEST 2: TERMINAL CALCULATOR ===")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="python3 -c \"import sys; sys.path.append('/usr/local/bin'); exec(open('/usr/local/bin/terminal_calculator.py').read())\" 2>/dev/null || python3 -c \"print('Calculator simulation'); print('Enter: 2+3'); result=eval('2+3'); print(f'Result: {result}')\"",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        time.sleep(2)
        
        # Start live display for calculator
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Test Everything - Calculator",
            update_interval=0.3
        )
        display_id = display_result['display_id']
        time.sleep(2)
        
        print("Calculator should be running...")
        print("Try typing some calculations:")
        print("- Type: 5+3")
        print("- Press Enter")
        print("- Try: 10*7")
        print("- Press Enter")
        
        # Send some test calculations
        time.sleep(2)
        terminal_manager.send_input(session_id, "5+3\n")
        time.sleep(2)
        terminal_manager.send_input(session_id, "10*7\n")
        time.sleep(2)
        
        calculator_works = input("\nDoes the calculator work properly? (y/n): ").lower().strip()
        
        # Try to exit calculator
        terminal_manager.send_input(session_id, "exit\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "quit\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "\x03")  # Ctrl+C
        time.sleep(1)
        
        # Clean up second test
        live_manager.stop_display(display_id)
        terminal_manager.terminate_session(session_id)
        time.sleep(1)
        
        # Test 3: Quick vim test
        print("\n=== TEST 3: QUICK VIM TEST ===")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        time.sleep(1)
        
        # Start live display for vim
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Test Everything - Vim",
            update_interval=0.3
        )
        display_id = display_result['display_id']
        time.sleep(1)
        
        # Add some colored content first
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[31mShell content before vim\\033[0m'\n")
        time.sleep(1)
        
        print("Starting vim...")
        terminal_manager.send_input(session_id, "vim /tmp/test.txt\n")
        time.sleep(3)
        
        vim_clears = input("\nDid vim clear the screen (no shell content visible)? (y/n): ").lower().strip()
        
        # Exit vim
        terminal_manager.send_input(session_id, "\x1b:q!\n")  # Escape, :q!
        time.sleep(2)
        
        colors_restored = input("Are the shell colors restored after exiting vim? (y/n): ").lower().strip()
        
        # Final assessment
        print("\n" + "="*50)
        print("FINAL RESULTS:")
        print("="*50)
        print(f"Colors work: {'✅ PASS' if colors_work == 'y' else '❌ FAIL'}")
        print(f"Calculator works: {'✅ PASS' if calculator_works == 'y' else '❌ FAIL'}")
        print(f"Vim clears screen: {'✅ PASS' if vim_clears == 'y' else '❌ FAIL'}")
        print(f"Colors restored: {'✅ PASS' if colors_restored == 'y' else '❌ FAIL'}")
        
        all_passed = all(x == 'y' for x in [colors_work, calculator_works, vim_clears, colors_restored])
        
        print("\n" + "="*50)
        if all_passed:
            print("🎉 SUCCESS: Everything is working correctly!")
            print("   The terminal MCP server is ready for production use!")
        else:
            print("⚠️  PARTIAL SUCCESS: Some features need more work")
            if colors_work != 'y':
                print("   - Colors need fixing")
            if calculator_works != 'y':
                print("   - Calculator functionality needs fixing")
            if vim_clears != 'y':
                print("   - Vim screen clearing needs fixing")
            if colors_restored != 'y':
                print("   - Color restoration needs fixing")
        print("="*50)
        
    finally:
        # Final cleanup
        print("\nFinal cleanup...")
        try:
            if display_id:
                live_manager.stop_display(display_id)
            live_manager.cleanup()
            if session_id:
                terminal_manager.terminate_session(session_id)
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    test_everything_works()
