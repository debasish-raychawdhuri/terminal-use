#!/usr/bin/env python3
"""
Test color display in tkinter.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def test_color_display():
    """Test that colors display correctly in tkinter."""
    
    print("=== Testing Color Display in Tkinter ===")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Color Display Test")
    root.geometry("800x600")
    
    # Create text widget
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 10),
        bg='black',
        fg='white',
        insertbackground='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=80, height=24)
    
    # Add colorful content
    print("Adding colorful content...")
    test_content = """bash-5.1$ echo -e '\x1b[31mRed text\x1b[0m'
\x1b[31mRed text\x1b[0m
bash-5.1$ echo -e '\x1b[32mGreen text\x1b[0m'
\x1b[32mGreen text\x1b[0m
bash-5.1$ echo -e '\x1b[1;34mBold Blue text\x1b[0m'
\x1b[1;34mBold Blue text\x1b[0m
bash-5.1$ echo -e '\x1b[33mYellow text\x1b[0m'
\x1b[33mYellow text\x1b[0m"""
    
    emulator.process_content(test_content)
    
    # Render to tkinter
    print("Rendering to tkinter...")
    emulator.render_to_tkinter(text_widget)
    
    # Add instructions
    instruction_label = tk.Label(
        root, 
        text="Check if you can see RED, GREEN, BLUE, and YELLOW colored text above.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 12)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("Window opened. Check if colors are visible!")
    print("You should see:")
    print("- Red text")
    print("- Green text") 
    print("- Bold Blue text")
    print("- Yellow text")
    print()
    print("Close the window when you're done checking.")
    
    # Run the GUI
    root.mainloop()
    
    print("Test complete!")

if __name__ == "__main__":
    test_color_display()
