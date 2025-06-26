#!/usr/bin/env python3
"""
Debug the screen buffer transitions to understand what's happening.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def debug_screen_transitions():
    """Debug screen buffer transitions step by step."""
    
    print("=== Debugging Screen Buffer Transitions ===\n")
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=60, height=15)
    
    def show_screen_state(title):
        print(f"\n--- {title} ---")
        print(f"Alt screen active: {emulator.in_alt_screen}")
        print(f"Cursor: ({emulator.cursor_x}, {emulator.cursor_y})")
        print("Screen content:")
        for i, row in enumerate(emulator.screen[:8]):  # Show first 8 lines
            line = ''.join(cell.char for cell in row).rstrip()
            if line:
                colors = [cell.fg_color for cell in row if cell.char.strip()]
                has_colors = any(color != 'white' for color in colors)
                color_info = f" [colors: {set(colors)}]" if has_colors else ""
                print(f"  {i:2}: '{line}'{color_info}")
            else:
                print(f"  {i:2}: (empty)")
        print()
    
    # 1. Initial shell content
    print("1. Adding initial shell content...")
    shell_content = """bash-5.1$ echo -e '\x1b[31mRed line\x1b[0m'
\x1b[31mRed line\x1b[0m
bash-5.1$ echo -e '\x1b[32mGreen line\x1b[0m'
\x1b[32mGreen line\x1b[0m
bash-5.1$ ls --color=always
\x1b[01;34mfolder\x1b[0m  \x1b[01;32mscript.sh\x1b[0m
bash-5.1$ vim test.txt"""
    
    emulator.process_content(shell_content)
    show_screen_state("After shell content")
    
    # 2. Enter alternative screen (vim start)
    print("2. Entering alternative screen buffer...")
    vim_enter = "\x1b[?1049h"
    emulator.process_content(vim_enter)
    show_screen_state("After entering alt screen")
    
    # 3. Clear screen and position cursor
    print("3. Clearing screen and positioning cursor...")
    vim_clear = "\x1b[H\x1b[2J"
    emulator.process_content(vim_clear)
    show_screen_state("After screen clear")
    
    # 4. Add vim content
    print("4. Adding vim interface...")
    vim_content = """~
~
~
~
~
~
~
~
~
~
~
~
\x1b[13;1H"test.txt" [New File]"""
    emulator.process_content(vim_content)
    show_screen_state("After vim interface")
    
    # 5. Add some text in vim
    print("5. Adding text in vim...")
    emulator.process_content("\x1b[1;1H")  # Go to top
    emulator.process_content("Hello from vim!")
    emulator.process_content("\x1b[14;1H-- INSERT --")
    show_screen_state("After typing in vim")
    
    # 6. Exit alternative screen
    print("6. Exiting alternative screen buffer...")
    vim_exit = "\x1b[?1049l"
    emulator.process_content(vim_exit)
    show_screen_state("After exiting alt screen")
    
    # 7. Check if colors are preserved
    print("7. Color preservation check...")
    red_found = False
    green_found = False
    blue_found = False
    
    for row in emulator.screen[:8]:
        for cell in row:
            if cell.char.strip():
                if '#CD0000' in cell.fg_color or '#FF0000' in cell.fg_color:
                    red_found = True
                elif '#00CD00' in cell.fg_color or '#00FF00' in cell.fg_color:
                    green_found = True
                elif '#0000EE' in cell.fg_color or '#5C5CFF' in cell.fg_color:
                    blue_found = True
    
    print(f"Red colors preserved: {'✅' if red_found else '❌'}")
    print(f"Green colors preserved: {'✅' if green_found else '❌'}")
    print(f"Blue colors preserved: {'✅' if blue_found else '❌'}")
    
    # 8. Test what happens with additional content
    print("\n8. Adding new content after vim...")
    emulator.process_content("\nbash-5.1$ echo 'After vim'")
    emulator.process_content("\nAfter vim")
    show_screen_state("After new content")
    
    print("=== Debug Complete ===")

if __name__ == "__main__":
    debug_screen_transitions()
