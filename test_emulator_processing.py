#!/usr/bin/env python3
"""
Test if the terminal emulator processes the actual content correctly.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def test_emulator_processing():
    """Test emulator with the actual problematic content."""
    
    print("=== Testing Emulator Processing ===")
    
    # This is the actual content that was captured from the terminal
    actual_content = "\x1b]697;OSCUnlock=5db7aed37a6b48909fc241092ac49d0d\x07\x1b]697;Dir=/home/debasish/work/talentica/terminal-mcp-server\x07\x1b]697;Shell=bash\x07\x1b]697;ShellPath=/usr/bin/bash\x07\x1b]697;PID=3441358\x07\x1b]697;ExitCode=0\x07\x1b]697;TTY=/dev/pts/7\x07\x1b]697;Log=\x07\x1b]697;User=debasish\x07\x1b]697;OSCLock=5db7aed37a6b48909fc241092ac49d0d\x07\x1b]697;PreExec\x07\x1b]697;OSCLock=5db7aed37a6b48909fc241092ac49d0d\x07\x1b]697;PreExec\x07\x1b[?2004h\x1b]697;StartPrompt\x07(base) \x1b]0;debasish@DebasishC-UB: ~/work/talentica/terminal-mcp-server\x07\x1b[01;32mdebasish@DebasishC-UB\x1b[00m:\x1b[01;34m~/work/talentica/terminal-mcp-server\x1b[00m$ \x1b]697;EndPrompt\x07\x1b]697;NewCmd=5db7aed37a6b48909fc241092ac49d0d\x07echo -e '\\033[31mRed\\033[0m'\r\n\x1b[?2004l\r\x1b[31mRed\x1b[0m\r\n\x1b]697;OSCUnlock=5db7aed37a6b48909fc241092ac49d0d\x07\x1b]697;Dir=/home/debasish/work/talentica/terminal-mcp-server\x07\x1b]697;Shell=bash\x07\x1b]697;ShellPath=/usr/bin/bash\x07\x1b]697;PID=3441358\x07\x1b]697;ExitCode=0\x07\x1b]697;TTY=/dev/pts/7\x07\x1b]697;Log=\x07\x1b]697;User=debasish\x07\x1b[?2004h\x1b]697;StartPrompt\x07(base) \x1b]0;debasish@DebasishC-UB: ~/work/talentica/terminal-mcp-server\x07\x1b[01;32mdebasish@DebasishC-UB\x1b[00m:\x1b[01;34m~/work/talentica/terminal-mcp-server\x1b[00m$ \x1b]697;EndPrompt\x07\x1b]697;NewCmd=5db7aed37a6b48909fc241092ac49d0d\x07"
    
    print(f"Processing content length: {len(actual_content)}")
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=100, height=30)
    
    # Process the actual content
    print("Processing content through emulator...")
    emulator.process_content(actual_content)
    
    # Check what's in the screen buffer
    print("\nScreen buffer contents:")
    for i, row in enumerate(emulator.screen[:10]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            # Check for colors
            colors = [(cell.char, cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
            has_colors = any(color[1] != 'white' or color[2] != 'black' for color in colors)
            
            print(f"  Line {i}: '{line}' {'(HAS COLORS)' if has_colors else '(no colors)'}")
            
            if has_colors:
                # Show color details for first few characters
                color_details = colors[:5]
                print(f"    Color details: {color_details}")
            
            # Check for escape sequences in the text
            if '\x1b' in line or '\\033' in line:
                print(f"    ❌ CONTAINS ESCAPE SEQUENCES!")
    
    # Create tkinter window to show the result
    print("\nCreating visual display...")
    
    root = tk.Tk()
    root.title("Emulator Processing Test")
    root.geometry("1000x600")
    
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 10),
        bg='black',
        fg='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Render using the emulator
    emulator.render_to_tkinter(text_widget)
    
    # Add instructions
    instruction_label = tk.Label(
        root, 
        text="This shows the result of processing the actual terminal content.\nYou should see colored text (green username, blue path, red 'Red').\nIf you see escape sequences, the emulator is not working correctly.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("Window opened. Check if:")
    print("1. You see colored text (green username, blue path, red 'Red')")
    print("2. You DON'T see any escape sequences like \\x1b[31m")
    print("3. The text is clean and readable")
    
    # Run the GUI
    root.mainloop()
    
    print("Test complete!")

if __name__ == "__main__":
    test_emulator_processing()
