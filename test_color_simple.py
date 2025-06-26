#!/usr/bin/env python3
"""
Simple test for color display in tkinter.
"""

import tkinter as tk
from terminal_mcp_server.ansi_to_tkinter import ANSIToTkinter

def test_colors_simple():
    """Test colors in a simple tkinter window."""
    print("Testing colors in tkinter...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Color Test")
    root.geometry("800x600")
    root.configure(bg='black')
    
    # Create text widget
    text_widget = tk.Text(
        root,
        bg='black',
        fg='white',
        font=('Courier New', 12),
        wrap=tk.NONE
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Create ANSI converter
    converter = ANSIToTkinter(text_widget)
    
    # Test content with colors
    test_content = """Normal text
\x1b[31mRed text\x1b[0m
\x1b[32mGreen text\x1b[0m
\x1b[34mBlue text\x1b[0m
\x1b[1;33mBold Yellow text\x1b[0m
\x1b[35mMagenta text\x1b[0m
\x1b[36mCyan text\x1b[0m
Back to normal text"""
    
    print("Inserting colored content...")
    converter.clear_and_insert_with_colors(test_content)
    
    print("Color test window should now show colored text!")
    print("Close the window to continue...")
    
    root.mainloop()

if __name__ == "__main__":
    test_colors_simple()
