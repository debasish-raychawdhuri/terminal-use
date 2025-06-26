#!/usr/bin/env python3
"""
Test the improved live display with better escape sequence cleanup.
"""

import sys
import os
import time
import threading

# Add the terminal_mcp_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_improved_live():
    """Test the improved live display functionality."""
    
    print("=== Testing IMPROVED Live Display (No Junk Sequences) ===\n")
    
    # Initialize managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    try:
        # 1. Start a bash session
        print("1. Starting bash session...")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        print(f"Session ID: {session_id}")
        
        # 2. Start live display
        print("2. Starting live display...")
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Improved Live Display Test",
            update_interval=0.5
        )
        print(f"Live display started: {display_result['display_id']}")
        
        # 3. Test shell colors and commands
        print("3. Testing shell colors...")
        time.sleep(1)
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRed\\033[32m Green\\033[34m Blue\\033[0m Normal'\n")
        time.sleep(1)
        terminal_manager.send_input(session_id, "ls --color=always\n")
        time.sleep(1)
        
        print("4. Shell should show colored text with NO junk sequences. Now testing vim...")
        
        # 4. Test vim (which generates lots of escape sequences)
        terminal_manager.send_input(session_id, "vim /tmp/test_improved.txt\n")
        time.sleep(2)
        
        print("5. CHECK THE LIVE DISPLAY NOW:")
        print("   ✅ Should show vim interface with tildes (~)")
        print("   ✅ Should NOT show ANY escape sequences like '25h', '1049h', etc.")
        print("   ✅ Should show clean status line at bottom")
        print("   ✅ Should be properly formatted with no junk text")
        
        # 5. Interact with vim
        print("6. Interacting with vim...")
        time.sleep(1)
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "This is clean text with no escape sequences!")
        time.sleep(1)
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(0.5)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(2)
        
        print("   Should show text in vim and '-- INSERT --' mode indicator")
        print("7. Should be back to shell now...")
        
        # 6. Final verification
        print("8. FINAL VERIFICATION:")
        print("   ✅ Vim interface was clean (no garbled text)")
        print("   ✅ No escape sequences visible as text")
        print("   ✅ Proper screen clearing and updates")
        print("   ✅ Colors preserved in both shell and vim")
        print("   ✅ Clean transition back to shell")
        print("   ✅ NO JUNK SEQUENCES AT THE END!")
        
        print("\nIf the live display shows clean output with no junk sequences,")
        print("then the improved escape sequence handling is working!")
        print("Press Enter to stop the test...")
        input()
        
    finally:
        # Cleanup
        print("Cleaning up...")
        live_manager.cleanup()
        terminal_manager.terminate_session(session_id)

if __name__ == "__main__":
    test_improved_live()
