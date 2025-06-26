#!/usr/bin/env python3
"""
Debug why colors are not showing up at all.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def debug_color_issue():
    """Debug color processing step by step."""
    
    print("=== Debugging Color Issue ===\n")
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=60, height=10)
    
    # Test simple color sequence
    print("1. Testing simple red text...")
    test_content = "\x1b[31mRed text\x1b[0m"
    print(f"   Input: {repr(test_content)}")
    
    emulator.process_content(test_content)
    
    # Check what's in the screen buffer
    print("   Screen buffer content:")
    for i, row in enumerate(emulator.screen[:3]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
            print(f"     Line {i}: '{line}'")
            print(f"     Colors: {colors}")
    
    print(f"   Current fg color: {emulator.current_fg}")
    print(f"   Current bg color: {emulator.current_bg}")
    
    # Test with bold red
    print("\n2. Testing bold red text...")
    emulator = TerminalScreenEmulator(width=60, height=10)
    test_content2 = "\x1b[1;31mBold Red text\x1b[0m"
    print(f"   Input: {repr(test_content2)}")
    
    emulator.process_content(test_content2)
    
    print("   Screen buffer content:")
    for i, row in enumerate(emulator.screen[:3]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color, cell.bg_color, cell.bold) for cell in row if cell.char.strip()]
            print(f"     Line {i}: '{line}'")
            print(f"     Colors: {colors}")
    
    # Test the actual shell command
    print("\n3. Testing actual shell command...")
    emulator = TerminalScreenEmulator(width=60, height=10)
    shell_content = "bash-5.1$ echo -e '\\033[31mRed text\\033[0m'\n\x1b[31mRed text\x1b[0m\nbash-5.1$ "
    print(f"   Input: {repr(shell_content[:100])}...")
    
    emulator.process_content(shell_content)
    
    print("   Screen buffer content:")
    for i, row in enumerate(emulator.screen[:5]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color) for cell in row if cell.char.strip()]
            has_colors = any(color != 'white' for _, color in colors)
            print(f"     Line {i}: '{line}' {'(HAS COLORS)' if has_colors else '(NO COLORS)'}")
            if has_colors:
                print(f"       Color details: {colors[:10]}")  # Show first 10 chars
    
    # Test if the issue is in the regex pattern
    print("\n4. Testing ANSI sequence detection...")
    import re
    
    pattern = r'(\x1b\[[?!>]?[0-9;:<=>?]*[a-zA-Z@`]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()#%*+].|\x1b[DEHMNOVWXZ78]|\x1b=|\x1b>)'
    test_sequences = [
        "\x1b[31m",
        "\x1b[1;31m", 
        "\x1b[0m",
        "\x1b[?25h",
        "\x1b[H"
    ]
    
    for seq in test_sequences:
        matches = re.findall(pattern, seq + "text")
        print(f"   Sequence {repr(seq)}: matches = {matches}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_color_issue()
