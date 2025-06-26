#!/usr/bin/env python3
"""
Test script to verify that escape sequence cleanup is working properly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def test_escape_cleanup():
    """Test that various escape sequences are properly handled."""
    
    print("=== Testing Escape Sequence Cleanup ===\n")
    
    # Create a small terminal emulator
    emulator = TerminalScreenEmulator(width=40, height=10)
    
    # Test various problematic sequences
    test_cases = [
        # Basic color with junk at end
        "\x1b[31mRed text\x1b[0m\x1b=\x1b>",
        
        # Vim-style sequences
        "\x1b[?25h\x1b[?1049h\x1b[H\x1b[2JVim content\x1b[?25l",
        
        # Mixed sequences with text
        "Normal \x1b[32mgreen\x1b[0m text\x1b(B\x1b)0 more text",
        
        # Complex cursor positioning
        "\x1b[1;1H\x1b[KLine 1\x1b[2;1H\x1b[KLine 2\x1b[?12h\x1b[?25h",
        
        # OSC sequences (window titles)
        "\x1b]0;Window Title\x07Normal text after title",
        
        # Character set sequences
        "\x1b(B\x1b)0\x1b*B\x1b+BNormal text",
    ]
    
    for i, test_content in enumerate(test_cases, 1):
        print(f"{i}. Testing: {repr(test_content[:50])}...")
        
        # Reset emulator
        emulator = TerminalScreenEmulator(width=40, height=10)
        
        # Process the content
        emulator.process_content(test_content)
        
        # Get the rendered text
        rendered_lines = []
        for row in emulator.screen:
            line = ''.join(cell.char for cell in row).rstrip()
            if line:  # Only include non-empty lines
                rendered_lines.append(line)
        
        rendered_text = '\n'.join(rendered_lines)
        
        print(f"   Result: {repr(rendered_text)}")
        
        # Check for any remaining escape sequences
        has_escapes = '\x1b' in rendered_text
        if has_escapes:
            print(f"   ❌ STILL HAS ESCAPE SEQUENCES!")
            # Show where they are
            for j, char in enumerate(rendered_text):
                if char == '\x1b':
                    context = rendered_text[max(0, j-5):j+10]
                    print(f"      Escape at position {j}: {repr(context)}")
        else:
            print(f"   ✅ Clean - no escape sequences")
        
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_escape_cleanup()
