#!/usr/bin/env python3
"""
Debug tkinter color rendering step by step.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def debug_tkinter_colors():
    """Debug tkinter color rendering."""
    
    print("=== Debugging Tkinter Color Rendering ===")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Debug Color Rendering")
    root.geometry("800x400")
    
    # Create text widget
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 12),
        bg='black',
        fg='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Test 1: Direct tkinter color tags
    print("Test 1: Direct tkinter color application...")
    text_widget.insert(tk.END, "Direct Red Text\n", "red_tag")
    text_widget.insert(tk.END, "Direct Green Text\n", "green_tag")
    text_widget.insert(tk.END, "Direct Blue Text\n", "blue_tag")
    
    # Configure the tags
    text_widget.tag_configure("red_tag", foreground="#FF0000")
    text_widget.tag_configure("green_tag", foreground="#00FF00")
    text_widget.tag_configure("blue_tag", foreground="#0000FF")
    
    text_widget.insert(tk.END, "\n--- Terminal Emulator Test ---\n")
    
    # Test 2: Through terminal emulator
    print("Test 2: Through terminal emulator...")
    emulator = TerminalScreenEmulator(width=60, height=10)
    
    # Simple red text
    emulator.process_content("\x1b[31mEmulator Red Text\x1b[0m\n")
    emulator.process_content("\x1b[32mEmulator Green Text\x1b[0m\n")
    emulator.process_content("\x1b[34mEmulator Blue Text\x1b[0m\n")
    
    # Debug: Check what's in the screen buffer
    print("Screen buffer contents:")
    for i, row in enumerate(emulator.screen[:5]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
            print(f"  Line {i}: '{line}'")
            print(f"    Colors: {colors[:5]}")  # Show first 5 chars
    
    # Custom render with debug output
    print("Rendering with debug output...")
    
    # Enable editing
    text_widget.configure(state=tk.NORMAL)
    
    tag_counter = 0
    for y, row in enumerate(emulator.screen):
        line_text = ""
        current_attrs = None
        
        for x, cell in enumerate(row):
            attrs = (cell.fg_color, cell.bg_color, cell.bold, cell.underline)
            if attrs != current_attrs:
                # Insert accumulated text with previous attributes
                if line_text and current_attrs:
                    tag_name = f"debug_tag_{tag_counter}"
                    tag_counter += 1
                    
                    fg_color, bg_color, bold, underline = current_attrs
                    print(f"    Creating tag {tag_name}: fg={fg_color}, bg={bg_color}, bold={bold}")
                    
                    # Configure tag
                    font_config = ('Courier New', 12)
                    if bold and underline:
                        font_config = ('Courier New', 12, 'bold', 'underline')
                    elif bold:
                        font_config = ('Courier New', 12, 'bold')
                    elif underline:
                        font_config = ('Courier New', 12, 'underline')
                    
                    text_widget.tag_configure(
                        tag_name,
                        foreground=fg_color,
                        background=bg_color,
                        font=font_config
                    )
                    
                    text_widget.insert(tk.END, line_text, tag_name)
                    print(f"    Inserted '{line_text}' with tag {tag_name}")
                    line_text = ""
                current_attrs = attrs
            
            line_text += cell.char
        
        # Insert remaining text for this line
        if line_text:
            tag_name = f"debug_tag_{tag_counter}"
            tag_counter += 1
            
            if current_attrs:
                fg_color, bg_color, bold, underline = current_attrs
                print(f"    Creating final tag {tag_name}: fg={fg_color}, bg={bg_color}, bold={bold}")
                
                font_config = ('Courier New', 12)
                if bold and underline:
                    font_config = ('Courier New', 12, 'bold', 'underline')
                elif bold:
                    font_config = ('Courier New', 12, 'bold')
                elif underline:
                    font_config = ('Courier New', 12, 'underline')
                
                text_widget.tag_configure(
                    tag_name,
                    foreground=fg_color,
                    background=bg_color,
                    font=font_config
                )
                
                text_widget.insert(tk.END, line_text, tag_name)
                print(f"    Inserted final '{line_text.rstrip()}' with tag {tag_name}")
        
        # Add newline except for last line
        if y < len(emulator.screen) - 1:
            text_widget.insert(tk.END, '\n')
    
    # Disable editing
    text_widget.configure(state=tk.DISABLED)
    
    # Add instructions
    instruction_label = tk.Label(
        root, 
        text="Check console output for debug info. You should see:\n1. Direct colored text at top\n2. Terminal emulator colored text below\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("\nWindow opened. Check if ANY colors are visible!")
    print("The direct tkinter colors should definitely work.")
    print("If even those don't work, there's a tkinter configuration issue.")
    
    # Run the GUI
    root.mainloop()
    
    print("Debug complete!")

if __name__ == "__main__":
    debug_tkinter_colors()
