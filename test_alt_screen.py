#!/usr/bin/env python3
"""
Test alternative screen buffer functionality (vim screen clearing and restoration).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def test_alt_screen_buffer():
    """Test that alternative screen buffer works correctly."""
    
    print("=== Testing Alternative Screen Buffer ===\n")
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=40, height=10)
    
    # 1. Add some colored content to the main screen
    print("1. Adding colored content to main screen...")
    emulator.process_content("\x1b[31mRed line 1\x1b[0m\n")
    emulator.process_content("\x1b[32mGreen line 2\x1b[0m\n")
    emulator.process_content("\x1b[34mBlue line 3\x1b[0m\n")
    emulator.process_content("Normal line 4\n")
    
    # Show main screen
    print("Main screen content:")
    for i, row in enumerate(emulator.screen[:5]):  # Show first 5 lines
        line = ''.join(cell.char for cell in row).rstrip()
        colors = [(cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
        if line:
            print(f"  Line {i}: '{line}' (colors: {colors[:3] if colors else 'none'})")
    
    print(f"Alt screen active: {emulator.in_alt_screen}")
    
    # 2. Enter alternative screen buffer (like vim does)
    print("\n2. Entering alternative screen buffer...")
    emulator.process_content("\x1b[?1049h")  # Enter alt screen
    emulator.process_content("\x1b[H\x1b[2J")  # Clear screen and go to top
    
    print(f"Alt screen active: {emulator.in_alt_screen}")
    
    # Show that screen is now clear
    print("Alt screen content (should be empty):")
    for i, row in enumerate(emulator.screen[:5]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            print(f"  Line {i}: '{line}'")
        else:
            print(f"  Line {i}: (empty)")
    
    # 3. Add vim-like content
    print("\n3. Adding vim-like content...")
    emulator.process_content("~\n~\n~\n")
    emulator.process_content("\x1b[10;1H")  # Go to bottom
    emulator.process_content("\x1b[7m-- INSERT --\x1b[0m")  # Status line
    
    print("Vim screen content:")
    for i, row in enumerate(emulator.screen):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            print(f"  Line {i}: '{line}'")
    
    # 4. Exit alternative screen buffer
    print("\n4. Exiting alternative screen buffer...")
    emulator.process_content("\x1b[?1049l")  # Exit alt screen
    
    print(f"Alt screen active: {emulator.in_alt_screen}")
    
    # Show that original content is restored
    print("Restored main screen content:")
    for i, row in enumerate(emulator.screen[:5]):
        line = ''.join(cell.char for cell in row).rstrip()
        colors = [(cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
        if line:
            print(f"  Line {i}: '{line}' (colors: {colors[:3] if colors else 'none'})")
    
    # 5. Verify colors are preserved
    print("\n5. Verification:")
    line1_colors = [cell.fg_color for cell in emulator.screen[0] if cell.char.strip()]
    line2_colors = [cell.fg_color for cell in emulator.screen[1] if cell.char.strip()]
    line3_colors = [cell.fg_color for cell in emulator.screen[2] if cell.char.strip()]
    
    print(f"Line 1 colors: {line1_colors}")
    print(f"Line 2 colors: {line2_colors}")
    print(f"Line 3 colors: {line3_colors}")
    
    # Check if colors are preserved
    has_red = any('#CD0000' in str(color) or '#FF0000' in str(color) for color in line1_colors)
    has_green = any('#00CD00' in str(color) or '#00FF00' in str(color) for color in line2_colors)
    has_blue = any('#0000EE' in str(color) or '#5C5CFF' in str(color) for color in line3_colors)
    
    print(f"\n✅ Red preserved: {has_red}")
    print(f"✅ Green preserved: {has_green}")
    print(f"✅ Blue preserved: {has_blue}")
    
    if has_red and has_green and has_blue:
        print("\n🎉 SUCCESS: Alternative screen buffer works correctly!")
        print("   - Screen clears when entering vim")
        print("   - Original content restored when exiting")
        print("   - Colors are preserved")
    else:
        print("\n❌ FAILURE: Colors were not preserved properly")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_alt_screen_buffer()
