#!/usr/bin/env python3
"""
Test that escape sequences are properly filtered while preserving colors.
"""

import tkinter as tk
from terminal_mcp_server.ansi_to_tkinter import ANSIToTkinter

def test_escape_filtering():
    """Test escape sequence filtering."""
    print("Testing escape sequence filtering...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Escape Sequence Filtering Test")
    root.geometry("900x600")
    root.configure(bg='black')
    
    # Create text widget
    text_widget = tk.Text(
        root,
        bg='black',
        fg='white',
        font=('Courier New', 10),
        wrap=tk.NONE
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Create ANSI converter
    converter = ANSIToTkinter(text_widget)
    
    # Test content with colors AND problematic escape sequences
    test_content = """Normal text
\x1b[31mRED TEXT\x1b[0m - this should be red
\x1b]697;OSCUnlock=test\x07This text should appear (OSC sequence filtered)
\x1b[32mGREEN TEXT\x1b[0m - this should be green
\x1b[?2004hThis should appear (bracketed paste mode filtered)
\x1b[34mBLUE TEXT\x1b[0m - this should be blue
\x1b]0;Window Title\x07This should appear (title sequence filtered)
\x1b[1;33mBOLD YELLOW\x1b[0m - this should be bold yellow
\x1b[?25hThis should appear (cursor show filtered)
\x1b[35mMAGENTA\x1b[0m - this should be magenta
\x1b[2JThis should appear (clear screen filtered)
\x1b[HThis should appear (cursor home filtered)
Final normal text"""
    
    print("Content includes:")
    print("- Color sequences (should render as colors)")
    print("- OSC sequences (should be filtered out)")
    print("- Cursor control sequences (should be filtered out)")
    print("- Mode setting sequences (should be filtered out)")
    
    converter.clear_and_insert_with_colors(test_content)
    
    print("\nIn the window, you should see:")
    print("✓ Colored text (RED, GREEN, BLUE, BOLD YELLOW, MAGENTA)")
    print("✓ Normal text without escape sequences visible")
    print("✗ NO literal escape sequences like \\x1b[?2004h or \\x1b]697")
    
    print("\nClose the window when done testing.")
    root.mainloop()

if __name__ == "__main__":
    test_escape_filtering()
