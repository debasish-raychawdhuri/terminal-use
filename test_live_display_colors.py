#!/usr/bin/env python3
"""
Test colors using the exact same code path as live display.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_screen_emulator import TerminalScreenEmulator

def test_live_display_colors():
    """Test colors using the same approach as live display."""
    
    print("=== Testing Live Display Color Path ===")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Live Display Color Test")
    root.geometry("800x600")
    
    # Create text widget with same settings as live display
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 10),
        bg='black',
        fg='white',
        insertbackground='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Simulate the exact content that would come from a shell session
    shell_content = """bash-5.1$ echo -e '\x1b[31mRed text\x1b[0m'
\x1b[31mRed text\x1b[0m
bash-5.1$ echo -e '\x1b[32mGreen text\x1b[0m'
\x1b[32mGreen text\x1b[0m
bash-5.1$ echo -e '\x1b[1;34mBold Blue text\x1b[0m'
\x1b[1;34mBold Blue text\x1b[0m
bash-5.1$ ls --color=always
\x1b[01;34mfolder\x1b[0m  \x1b[01;32mscript.sh\x1b[0m  \x1b[01;31mfile.txt\x1b[0m
bash-5.1$ """
    
    print("Simulating shell session content...")
    print("Content length:", len(shell_content))
    
    # Use the EXACT same approach as live display for shell sessions
    is_tui = False  # Shell session
    
    if not is_tui:
        # For shell sessions, create fresh emulator each time
        # This is exactly what live display does
        actual_width, actual_height = 80, 24  # Default dimensions
        terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
        terminal_emulator.process_content(shell_content)
        print(f"Shell session - fresh emulator: {actual_width}x{actual_height}")
    
    print(f"Processing content. TUI: {is_tui}, Length: {len(shell_content)}")
    
    # Render to the text widget - EXACT same call as live display
    terminal_emulator.render_to_tkinter(text_widget)
    
    print("Terminal emulation completed successfully")
    
    # Add debug info
    debug_info = tk.Text(root, height=8, bg='lightgray', font=('Arial', 9))
    debug_info.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    debug_text = """DEBUG INFO:
This uses the EXACT same code path as the live terminal display.
You should see:
- Red text
- Green text  
- Bold Blue text
- Colored directory listing (blue folder, green script.sh, red file.txt)

If you don't see colors here, then the live display won't show colors either.
Close window when done checking."""
    
    debug_info.insert(tk.END, debug_text)
    debug_info.configure(state=tk.DISABLED)
    
    print("\nWindow opened with EXACT live display code path!")
    print("If colors don't work here, they won't work in live display either.")
    
    # Run the GUI
    root.mainloop()
    
    print("Test complete!")

if __name__ == "__main__":
    test_live_display_colors()
