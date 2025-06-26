#!/usr/bin/env python3
"""
Test using the exact same approach as live display to find the color issue.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.terminal_screen_emulator import TerminalScreenEmulator

def test_live_display_exact():
    """Test using the exact same approach as live display."""
    
    print("=== Testing Live Display Exact Approach ===")
    
    # Step 1: Get real terminal content (same as live display)
    terminal_manager = TerminalManager()
    session_id = None
    
    try:
        # Start session and get content
        print("1. Getting real terminal content...")
        session_id = terminal_manager.generate_session_id()
        result = terminal_manager.run_command(
            command="bash",
            session_id=session_id,
            use_terminal_emulator=True,
            terminal_emulator="tmux"
        )
        time.sleep(1)
        
        # Send color command
        terminal_manager.send_input(session_id, "echo -e '\\033[31mRed\\033[0m'\n")
        time.sleep(2)
        
        # Get content exactly like live display does
        session_data = terminal_manager.get_session_output(session_id, raw_output=True)
        content = session_data['output'] if session_data else ""
        
        print(f"Content length: {len(content)}")
        ansi_count = content.count('\x1b')
        print(f"Content has {ansi_count} ANSI sequences")
        
    finally:
        if session_id:
            terminal_manager.terminate_session(session_id)
    
    # Step 2: Process exactly like live display
    print("2. Processing exactly like live display...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Live Display Exact Test")
    root.geometry("1000x600")
    
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 10),
        bg='black',
        fg='white',
        insertbackground='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Create terminal emulator exactly like live display
    actual_width, actual_height = 80, 24  # Default dimensions
    terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
    
    print("3. Processing content through emulator...")
    terminal_emulator.process_content(content)
    
    print("4. Rendering to tkinter...")
    terminal_emulator.render_to_tkinter(text_widget)
    
    # Debug: Check what's in the screen buffer
    print("5. Checking screen buffer...")
    red_found = False
    for i, row in enumerate(terminal_emulator.screen[:10]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line and 'Red' in line:
            colors = [(cell.char, cell.fg_color) for cell in row if cell.char.strip()]
            red_colors = [color for char, color in colors if color != 'white']
            if red_colors:
                red_found = True
                print(f"  Found 'Red' on line {i} with colors: {red_colors}")
            else:
                print(f"  Found 'Red' on line {i} but NO colors applied")
    
    if not red_found:
        print("  'Red' text not found in screen buffer")
    
    # Instructions
    instruction_label = tk.Label(
        root, 
        text="This uses the EXACT same process as live display.\nYou should see the word 'Red' in RED color.\nIf 'Red' appears but is not red, the emulator color processing is broken.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("\nWindow opened with EXACT live display process!")
    print("Check if the word 'Red' appears in red color.")
    print("If it's white instead of red, we found the exact issue.")
    
    # Run the GUI
    root.mainloop()
    
    print("Test complete!")

if __name__ == "__main__":
    test_live_display_exact()
