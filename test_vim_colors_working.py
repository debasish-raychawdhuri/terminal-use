#!/usr/bin/env python3
"""
Test vim workflow now that colors are working.
"""

import sys
import os
import time

# Add the terminal_mcp_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_vim_colors_working():
    """Test vim workflow now that colors are confirmed working."""
    
    print("=== TESTING VIM WITH WORKING COLORS ===")
    print()
    print("Since colors are now working in tkinter, let's test:")
    print("1. Colorful shell content displays properly")
    print("2. Vim clears the screen completely")
    print("3. Colors are preserved when exiting vim")
    print("4. No garbled text or escape sequences")
    print()
    
    # Initialize managers
    terminal_manager = TerminalManager()
    live_manager = LiveTerminalManager()
    
    session_id = None
    display_id = None
    
    try:
        # 1. Start bash session
        print("1. Starting bash session...")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        print(f"   Session ID: {session_id}")
        time.sleep(1)
        
        # 2. Start live display
        print("2. Starting live display...")
        display_result = live_manager.show_session_live(
            session_id=session_id,
            terminal_manager=terminal_manager,
            title="Vim Test - Colors Working!",
            update_interval=0.3
        )
        display_id = display_result['display_id']
        print(f"   Live display ID: {display_id}")
        time.sleep(1)
        
        # 3. Create colorful shell content
        print("3. Creating colorful shell content...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(0.5)
        
        # Add very distinctive colored content
        terminal_manager.send_input(session_id, "echo -e '\\033[1;31m🔴 RED: This should be bright red\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32m🟢 GREEN: This should be bright green\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;34m🔵 BLUE: This should be bright blue\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33m🟡 YELLOW: This should be bright yellow\\033[0m'\n")
        time.sleep(0.5)
        
        # Add directory listing with colors
        terminal_manager.send_input(session_id, "ls --color=always /bin | head -3\n")
        time.sleep(1)
        
        print("\n   ✓ Colorful shell content created")
        print("   → Check live display: Should show BRIGHT COLORED text with emojis")
        
        input("\nPress Enter when you can see the bright colored text...")
        
        # 4. Start vim
        print("\n4. Starting vim...")
        terminal_manager.send_input(session_id, "vim /tmp/vim_color_test.txt\n")
        time.sleep(3)  # Give vim time to fully initialize
        
        print("\n   🔍 CRITICAL CHECK - Look at the live display NOW:")
        print("   ✅ Screen should be COMPLETELY CLEAR of all colored text")
        print("   ✅ NO red, green, blue, or yellow text should be visible")
        print("   ✅ NO emojis should be visible")
        print("   ✅ Should only show vim interface with tildes (~)")
        print("   ✅ Should have clean vim status line")
        print("   ❌ If you see ANY shell content, vim screen clearing failed")
        
        vim_cleared = input("\nDid vim completely clear all the colored text? (y/n): ").lower().strip()
        
        # 5. Type in vim to verify it's working
        print("\n5. Testing vim functionality...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "Testing vim with working colors...")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nThis text should appear cleanly.")
        time.sleep(1)
        
        print("   → Should show text being typed in vim with '-- INSERT --'")
        
        input("\nPress Enter when you've verified vim is working...")
        
        # 6. Exit vim
        print("\n6. Exiting vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(0.5)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(3)  # Give time for screen restoration
        
        print("\n   🔍 CRITICAL CHECK - Look at the live display NOW:")
        print("   ✅ Should be back to shell")
        print("   ✅ ALL original colors should be restored:")
        print("      - 🔴 RED text with emoji")
        print("      - 🟢 GREEN text with emoji")
        print("      - 🔵 BLUE text with emoji")
        print("      - 🟡 YELLOW text with emoji")
        print("      - Colored directory listing")
        print("   ❌ If any colors are missing, color preservation failed")
        
        colors_restored = input("\nAre ALL the original colors restored? (y/n): ").lower().strip()
        
        # 7. Test new colors work
        print("\n7. Testing new colors after vim...")
        terminal_manager.send_input(session_id, "echo -e '\\033[1;35m🟣 MAGENTA: Post-vim test\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;36m🔷 CYAN: Everything works!\\033[0m'\n")
        time.sleep(1)
        
        new_colors_work = input("\nDo the new magenta and cyan colors display correctly? (y/n): ").lower().strip()
        
        # 8. Final assessment
        print("\n" + "="*60)
        print("FINAL ASSESSMENT:")
        print("="*60)
        
        print(f"✅ Vim screen clearing: {'PASS' if vim_cleared == 'y' else 'FAIL'}")
        print(f"✅ Color restoration: {'PASS' if colors_restored == 'y' else 'FAIL'}")
        print(f"✅ New colors work: {'PASS' if new_colors_work == 'y' else 'FAIL'}")
        
        all_passed = all(x == 'y' for x in [vim_cleared, colors_restored, new_colors_work])
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 SUCCESS: All vim fixes are working perfectly!")
            print("   ✅ Colors display correctly in live terminal")
            print("   ✅ Vim properly clears the screen")
            print("   ✅ Colors are preserved when exiting vim")
            print("   ✅ Terminal emulation is fully functional")
            print("\n   The terminal MCP server is now ready for production use!")
        else:
            print("⚠️  PARTIAL SUCCESS: Colors work but some issues remain")
            if vim_cleared != 'y':
                print("   ❌ Vim screen clearing needs more work")
            if colors_restored != 'y':
                print("   ❌ Color preservation needs more work")
            if new_colors_work != 'y':
                print("   ❌ Post-vim color functionality needs work")
        print("="*60)
        
    finally:
        # Cleanup
        print("\nCleaning up...")
        try:
            if display_id:
                live_manager.stop_live_display(display_id)
            live_manager.cleanup()
            if session_id:
                terminal_manager.terminate_session(session_id)
        except Exception as e:
            print(f"Cleanup error (normal): {e}")

if __name__ == "__main__":
    test_vim_colors_working()
