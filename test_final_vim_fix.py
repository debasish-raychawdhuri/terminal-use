#!/usr/bin/env python3
"""
Final test of the vim screen clearing and color preservation fixes.
"""

import sys
import os
import time

# Add the terminal_mcp_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_final_vim_fix():
    """Test the final vim fixes with live display."""
    
    print("=== Testing FINAL VIM FIXES ===")
    print("This test will verify:")
    print("1. Vim properly clears the screen when starting")
    print("2. Colors are preserved when exiting vim")
    print("3. No junk escape sequences appear")
    print()
    
    # Initialize managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    session_id = None
    
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
        time.sleep(1)
        
        # 2. Start live display
        print("2. Starting live display...")
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Final Vim Fix Test",
            update_interval=0.3
        )
        print(f"Live display started: {display_result['display_id']}")
        time.sleep(1)
        
        # 3. Create colorful shell content
        print("3. Creating colorful shell content...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[31m=== RED HEADER ===\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGreen: This is green text\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBlue: This is blue text\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[33mYellow: This is yellow text\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "ls --color=always /\n")
        time.sleep(1)
        
        print("4. LOOK AT THE LIVE DISPLAY NOW:")
        print("   ✅ Should show colorful shell output")
        print("   ✅ Red header, green/blue/yellow text")
        print("   ✅ Colored directory listing")
        print()
        
        input("Press Enter when you've seen the colorful shell content...")
        
        # 4. Start vim
        print("5. Starting vim...")
        terminal_manager.send_input(session_id, "vim /tmp/test_vim_fix.txt\n")
        time.sleep(2)
        
        print("6. CHECK THE LIVE DISPLAY NOW:")
        print("   ✅ Screen should be COMPLETELY CLEAR")
        print("   ✅ Should show vim interface with tildes (~)")
        print("   ✅ NO shell content should be visible")
        print("   ✅ Should have clean vim status line")
        print("   ✅ NO escape sequences like '25h' or '1049h'")
        print()
        
        input("Press Enter when you've verified vim cleared the screen...")
        
        # 5. Type in vim
        print("7. Typing in vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "This text was typed in vim!")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nLine 2 in vim")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nLine 3 in vim")
        time.sleep(1)
        
        print("8. Should show text in vim with '-- INSERT --' indicator")
        print()
        
        input("Press Enter when you've seen the vim content...")
        
        # 6. Exit vim
        print("9. Exiting vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(0.5)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(2)
        
        print("10. FINAL CHECK - LOOK AT THE LIVE DISPLAY:")
        print("    ✅ Should be back to shell")
        print("    ✅ ALL COLORS should be restored:")
        print("       - Red header")
        print("       - Green text")
        print("       - Blue text") 
        print("       - Yellow text")
        print("       - Colored directory listing")
        print("    ✅ NO junk escape sequences")
        print("    ✅ Clean transition from vim back to shell")
        print()
        
        input("Press Enter when you've verified colors are restored...")
        
        # 7. Final verification
        print("11. Adding more content to verify everything works...")
        terminal_manager.send_input(session_id, "echo -e '\\033[35mMagenta: Colors still work!\\033[0m'\n")
        time.sleep(1)
        
        print("12. FINAL ASSESSMENT:")
        print("    If you saw:")
        print("    ✅ Colorful shell content initially")
        print("    ✅ Vim completely cleared the screen")
        print("    ✅ Clean vim interface with no junk")
        print("    ✅ All colors restored after exiting vim")
        print("    ✅ New colors still work after vim")
        print()
        print("    Then the vim fixes are WORKING PERFECTLY! 🎉")
        print()
        
        input("Press Enter to finish the test...")
        
    finally:
        # Cleanup
        print("Cleaning up...")
        if session_id:
            try:
                live_manager.cleanup()
                terminal_manager.terminate_session(session_id)
            except Exception as e:
                print(f"Cleanup error (normal): {e}")

if __name__ == "__main__":
    test_final_vim_fix()
