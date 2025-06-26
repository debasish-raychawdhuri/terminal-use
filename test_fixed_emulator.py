#!/usr/bin/env python3
"""
Test the fixed terminal emulator with the problematic sequence.
"""

import tkinter as tk
from terminal_mcp_server.terminal_screen_emulator import TerminalScreenEmulator

def test_fixed_emulator():
    """Test the fixed emulator with the 25h sequence."""
    print("Testing fixed terminal emulator...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Fixed Emulator Test")
    root.geometry("800x600")
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
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(80, 24)
    
    # Test content that was causing problems (from debug output)
    problematic_content = """\x1b[?25h
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
~
~
~
~
~
"debug_live.txt" [New]                                                            0,0-1         All"""
    
    print("Processing problematic content...")
    print(f"Content starts with: {repr(problematic_content[:50])}")
    
    emulator.process_content(problematic_content)
    emulator.render_to_tkinter(text_widget)
    
    print("Check the window:")
    print("✓ Should NOT show '25h' at the top")
    print("✓ Should show clean vim interface with tildes")
    print("✓ Should show status line at bottom")
    
    # Test another problematic sequence
    def test_cursor_sequences():
        test_content = """\x1b[2J\x1b[H\x1b[?25l\x1b[31mRed text\x1b[0m
\x1b[10;20H\x1b[?1000h\x1b[32mGreen at position\x1b[0m
\x1b[?25h\x1b[1;1HCursor shown"""
        
        emulator.process_content(test_content)
        emulator.render_to_tkinter(text_widget)
    
    test_button = tk.Button(root, text="Test More Sequences", command=test_cursor_sequences)
    test_button.pack(pady=5)
    
    print("Click button to test more sequences.")
    print("Close window when done.")
    root.mainloop()

if __name__ == "__main__":
    test_fixed_emulator()
