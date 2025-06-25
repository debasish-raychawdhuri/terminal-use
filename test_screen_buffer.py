#!/usr/bin/env python3
"""
Test the screen buffer directly
"""

import sys
from terminal_mcp_server.screen_buffer import TerminalScreenBuffer

def main():
    """Test screen buffer functionality."""
    print("Testing screen buffer...")
    
    # Create a screen buffer
    buffer = TerminalScreenBuffer(10, 50)
    
    # Test simple text
    print("Test 1: Simple text")
    buffer.process_data("Hello World")
    content = buffer.get_screen_content()
    print(f"Content: '{content}'")
    print(f"Cursor: {buffer.get_cursor_position()}")
    
    # Test with ANSI sequences (like vim output)
    print("\nTest 2: ANSI sequences")
    vim_data = '\x1b[H\x1b[2J\x1b[40;1H"/tmp/test.txt" [New]\x1b[2;1H~\x1b[3;1H~\x1b[1;1HHello how are you\x1b[40;1H-- INSERT --'
    buffer.process_data(vim_data)
    content = buffer.get_screen_content()
    print(f"Content after ANSI:\n{content}")
    print(f"Cursor: {buffer.get_cursor_position()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
