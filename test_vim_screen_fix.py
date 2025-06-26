#!/usr/bin/env python3
"""
Test vim screen clearing and color preservation fixes.
"""

import sys
import os
import time

# Add the terminal_mcp_server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.live_terminal_display import LiveTerminalManager

def test_vim_screen_fix():
    """Test vim screen clearing and color preservation."""
    
    print("=== TESTING VIM SCREEN CLEARING & COLOR PRESERVATION ===")
    print()
    print("This test will verify:")
    print("1. Vim clears the screen completely (no shell content visible)")
    print("2. Colors are preserved when exiting vim")
    print("3. No garbled text or escape sequences")
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
            title="Vim Screen Fix Test",
            update_interval=0.3
        )
        display_id = display_result['display_id']
        print(f"   Live display ID: {display_id}")
        time.sleep(1)
        
        # 3. Create colorful shell content
        print("3. Creating colorful shell content...")
        terminal_manager.send_input(session_id, "clear\n")
        time.sleep(0.5)
        
        # Add distinctive colored content
        terminal_manager.send_input(session_id, "echo -e '\\033[1;31m████ RED HEADER ████\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;32m▓▓▓▓ GREEN LINE ▓▓▓▓\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;34m░░░░ BLUE TEXT ░░░░\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;33m▒▒▒▒ YELLOW INFO ▒▒▒▒\\033[0m'\n")
        time.sleep(0.5)
        
        # Add directory listing with colors
        terminal_manager.send_input(session_id, "ls --color=always /bin | head -3\n")
        time.sleep(1)
        
        print("\n   ✓ Colorful shell content created")
        print("   → Check live display: Should show colorful text with blocks/symbols")
        
        input("\nPress Enter when you see the colorful shell content...")
        
        # 4. Start vim
        print("\n4. Starting vim...")
        terminal_manager.send_input(session_id, "vim /tmp/vim_test.txt\n")
        time.sleep(3)  # Give vim time to fully initialize
        
        print("\n   CRITICAL CHECK - Look at the live display NOW:")
        print("   ✅ Screen should be COMPLETELY CLEAR")
        print("   ✅ NO red blocks, green blocks, blue text, or yellow text visible")
        print("   ✅ Should only show vim interface with tildes (~)")
        print("   ✅ Should have clean vim status line")
        print("   ❌ If you still see ANY shell content, the fix failed")
        
        input("\nPress Enter when you've checked if vim cleared the screen...")
        
        # 5. Type in vim to verify it's working
        print("\n5. Testing vim functionality...")
        terminal_manager.send_input(session_id, "i")  # Insert mode
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "Testing vim screen clearing...")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "\nThis should appear cleanly in vim.")
        time.sleep(1)
        
        print("   → Should show text being typed in vim with '-- INSERT --'")
        
        input("\nPress Enter when you've verified vim is working...")
        
        # 6. Exit vim
        print("\n6. Exiting vim...")
        terminal_manager.send_input(session_id, "\x1b")  # Escape
        time.sleep(0.5)
        terminal_manager.send_input(session_id, ":wq\n")  # Save and quit
        time.sleep(3)  # Give time for screen restoration
        
        print("\n   CRITICAL CHECK - Look at the live display NOW:")
        print("   ✅ Should be back to shell")
        print("   ✅ ALL original colors should be restored:")
        print("      - Red blocks (████ RED HEADER ████)")
        print("      - Green blocks (▓▓▓▓ GREEN LINE ▓▓▓▓)")
        print("      - Blue text (░░░░ BLUE TEXT ░░░░)")
        print("      - Yellow text (▒▒▒▒ YELLOW INFO ▒▒▒▒)")
        print("      - Colored directory listing")
        print("   ❌ If colors are missing or garbled, the fix failed")
        
        input("\nPress Enter when you've checked color restoration...")
        
        # 7. Test new colors work
        print("\n7. Testing new colors after vim...")
        terminal_manager.send_input(session_id, "echo -e '\\033[1;35m◆◆◆◆ MAGENTA POST-VIM ◆◆◆◆\\033[0m'\n")
        time.sleep(0.5)
        terminal_manager.send_input(session_id, "echo -e '\\033[1;36m◇◇◇◇ CYAN SUCCESS ◇◇◇◇\\033[0m'\n")
        time.sleep(1)
        
        print("   → Should show new magenta and cyan colored text")
        
        # 8. Final assessment
        print("\n" + "="*60)
        print("FINAL ASSESSMENT:")
        print("="*60)
        
        vim_cleared = input("Did vim completely clear the screen? (y/n): ").lower().strip()
        colors_restored = input("Were all colors restored after exiting vim? (y/n): ").lower().strip()
        no_garbling = input("Was there no garbled text or escape sequences? (y/n): ").lower().strip()
        new_colors_work = input("Do new colors work after vim? (y/n): ").lower().strip()
        
        print("\nRESULTS:")
        print(f"✅ Vim screen clearing: {'PASS' if vim_cleared == 'y' else 'FAIL'}")
        print(f"✅ Color restoration: {'PASS' if colors_restored == 'y' else 'FAIL'}")
        print(f"✅ No garbling: {'PASS' if no_garbling == 'y' else 'FAIL'}")
        print(f"✅ New colors work: {'PASS' if new_colors_work == 'y' else 'FAIL'}")
        
        all_passed = all(x == 'y' for x in [vim_cleared, colors_restored, no_garbling, new_colors_work])
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 SUCCESS: All vim fixes are working correctly!")
            print("   The terminal emulation is now properly handling:")
            print("   - Alternative screen buffer transitions")
            print("   - Color preservation across vim sessions")
            print("   - Clean screen clearing and restoration")
        else:
            print("❌ FAILURE: Some issues remain")
            print("   The terminal emulation needs further fixes")
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
    test_vim_screen_fix()
