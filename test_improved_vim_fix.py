#!/usr/bin/env python3
"""
Test the improved vim fix with better state management.
"""

import sys
import os
import time

# Add the terminal_mcp_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_improved_vim_fix():
    """Test the improved vim fixes."""
    
    print("=== Testing IMPROVED VIM FIXES ===")
    print("This test addresses the screen garbling issue by:")
    print("1. Better state management for TUI vs shell sessions")
    print("2. Incremental content processing for TUI apps")
    print("3. Fresh emulator for shell sessions to prevent state corruption")
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
            title="Improved Vim Fix Test - No Garbling",
            update_interval=0.4
        )
        print(f"Live display started: {display_result['display_id']}")
        time.sleep(1)
        
        # 3. Create colorful shell content
        print("3. Creating colorful shell content...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;31m=== COLORFUL SHELL TEST ===\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[32mGreen: File operations\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[34mBlue: Directory listing\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[33mYellow: System info\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "ls --color=always /usr/bin | head -5\n")
        time.sleep(1)
        
        print("\n4. VERIFY COLORFUL SHELL:")
        print("   ✅ Should show red header")
        print("   ✅ Should show green, blue, yellow text")
        print("   ✅ Should show colored directory listing")
        print("   ✅ All colors should be clean and vibrant")
        
        input("\nPress Enter when you've verified the colorful shell...")
        
        # 4. Start vim
        print("\n5. Starting vim...")
        terminal_manager.send_input(session_id, "vim /tmp/test_improved_vim.txt\n")
        time.sleep(3)  # Give vim time to fully start
        
        print("\n6. VERIFY VIM DISPLAY:")
        print("   ✅ Screen should be COMPLETELY CLEAR of shell content")
        print("   ✅ Should show vim interface with tildes (~)")
        print("   ✅ Should have vim status line at bottom")
        print("   ✅ NO shell colors or text should be visible")
        print("   ✅ NO escape sequences or garbled text")
        
        input("\nPress Enter when you've verified vim is clean...")
        
        # 5. Type in vim
        print("\n7. Typing in vim...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "Line 1: Testing vim display")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nLine 2: Colors should be preserved")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nLine 3: No garbling after exit")
        time.sleep(1)
        
        print("\n8. VERIFY VIM EDITING:")
        print("   ✅ Should show text being typed")
        print("   ✅ Should show '-- INSERT --' at bottom")
        print("   ✅ Text should appear cleanly")
        
        input("\nPress Enter when you've seen the vim editing...")
        
        # 6. Exit vim
        print("\n9. Exiting vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(0.5)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(3)  # Give time for vim to exit and screen to restore
        
        print("\n10. CRITICAL TEST - VERIFY SHELL RESTORATION:")
        print("    ✅ Should be back to shell prompt")
        print("    ✅ ALL ORIGINAL COLORS should be restored:")
        print("       - Red header text")
        print("       - Green 'File operations' text")
        print("       - Blue 'Directory listing' text") 
        print("       - Yellow 'System info' text")
        print("       - Colored directory listing")
        print("    ✅ NO garbled text or mixed vim/shell content")
        print("    ✅ NO escape sequences visible")
        print("    ✅ Clean, readable shell history")
        
        input("\nPress Enter when you've verified the shell restoration...")
        
        # 7. Test that colors still work
        print("\n11. Testing that colors still work after vim...")
        terminal_manager.send_input(session_id, "echo -e '\\033[35mMagenta: Post-vim test\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[36mCyan: Everything works!\\033[0m'\n")
        time.sleep(1)
        
        print("\n12. FINAL VERIFICATION:")
        print("    ✅ New colors should display correctly")
        print("    ✅ Shell should be fully functional")
        print("    ✅ No residual vim artifacts")
        
        print("\n" + "="*50)
        print("FINAL ASSESSMENT:")
        print("If you saw:")
        print("✅ Clean colorful shell initially")
        print("✅ Vim completely cleared the screen (no shell content visible)")
        print("✅ Clean vim interface with proper editing")
        print("✅ Perfect shell restoration with ALL colors preserved")
        print("✅ New colors working after vim exit")
        print()
        print("Then the vim garbling issue is COMPLETELY FIXED! 🎉")
        print("="*50)
        
        input("\nPress Enter to finish the test...")
        
    finally:
        # Cleanup
        print("\nCleaning up...")
        if session_id:
            try:
                live_manager.cleanup()
                terminal_manager.terminate_session(session_id)
            except Exception as e:
                print(f"Cleanup error (normal): {e}")

if __name__ == "__main__":
    test_improved_vim_fix()
