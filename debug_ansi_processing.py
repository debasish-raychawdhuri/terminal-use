#!/usr/bin/env python3
"""
Debug ANSI sequence processing to see why escape sequences are visible.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def debug_ansi_processing():
    """Debug ANSI sequence processing step by step."""
    
    print("=== Debugging ANSI Sequence Processing ===\n")
    
    # Test simple color sequence
    test_input = "\x1b[31mRed text\x1b[0m"
    print(f"Input: {repr(test_input)}")
    
    # Test the regex pattern
    pattern = r'(\x1b\[[?!>]?[0-9;:<=>?]*[a-zA-Z@`]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()#%*+].|\x1b[DEHMNOVWXZ78]|\x1b=|\x1b>)'
    parts = re.split(pattern, test_input)
    
    print(f"Regex split result: {parts}")
    print(f"Number of parts: {len(parts)}")
    
    for i, part in enumerate(parts):
        if part:
            is_ansi = part.startswith('\x1b')
            part_type = 'ANSI' if is_ansi else 'TEXT'
            print(f"  Part {i}: {repr(part)} - {part_type}")
    
    # Test with terminal emulator
    print("\n--- Terminal Emulator Processing ---")
    emulator = TerminalScreenEmulator(width=20, height=5)
    
    print("Before processing:")
    for i, row in enumerate(emulator.screen[:2]):
        line = ''.join(cell.char for cell in row).rstrip()
        print(f"  Row {i}: '{line}'")
    
    emulator.process_content(test_input)
    
    print("After processing:")
    for i, row in enumerate(emulator.screen[:2]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color) for cell in row if cell.char.strip()]
            print(f"  Row {i}: '{line}'")
            print(f"    Colors: {colors}")
    
    # Test with a more complex example
    print("\n--- Complex Example ---")
    complex_input = "bash-5.1$ echo -e '\\033[31mRed\\033[0m'\n\x1b[31mRed\x1b[0m\nbash-5.1$ "
    print(f"Complex input: {repr(complex_input[:50])}...")
    
    emulator2 = TerminalScreenEmulator(width=40, height=5)
    emulator2.process_content(complex_input)
    
    print("Result:")
    for i, row in enumerate(emulator2.screen[:4]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            # Check if line contains any escape sequences
            has_escapes = '\x1b' in line or '\\033' in line
            print(f"  Row {i}: '{line}' {'(HAS ESCAPES!)' if has_escapes else '(clean)'}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_ansi_processing()
