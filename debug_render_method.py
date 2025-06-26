#!/usr/bin/env python3
"""
Debug the render_to_tkinter method to see why colors aren't applied.
"""

import sys
import os
import tkinter as tk
from tkinter import scrolledtext

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def debug_render_method():
    """Debug the render method step by step."""
    
    print("=== Debugging Render Method ===")
    
    # Create simple content with red text
    content = "\x1b[31mRed\x1b[0m"
    
    # Create emulator and process
    emulator = TerminalScreenEmulator(width=20, height=5)
    emulator.process_content(content)
    
    # Check screen buffer
    print("Screen buffer after processing:")
    for i, row in enumerate(emulator.screen[:3]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [(cell.char, cell.fg_color, cell.bg_color) for cell in row if cell.char.strip()]
            print(f"  Row {i}: '{line}' - Colors: {colors}")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Debug Render Method")
    root.geometry("600x400")
    
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 12),
        bg='black',
        fg='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Manual render with debug output
    print("\nManual rendering with debug:")
    
    # Enable editing
    text_widget.configure(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    
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
                    print(f"  Creating tag {tag_name}: fg={fg_color}, bg={bg_color}, bold={bold}")
                    
                    # Configure tag
                    font_config = ('Courier New', 12)
                    if bold:
                        font_config = ('Courier New', 12, 'bold')
                    
                    print(f"  Configuring tag with foreground={fg_color}, background={bg_color}")
                    text_widget.tag_configure(
                        tag_name,
                        foreground=fg_color,
                        background=bg_color,
                        font=font_config
                    )
                    
                    print(f"  Inserting text '{line_text}' with tag {tag_name}")
                    text_widget.insert(tk.END, line_text, tag_name)
                    
                    # Verify tag was applied
                    tag_ranges = text_widget.tag_ranges(tag_name)
                    print(f"  Tag ranges: {tag_ranges}")
                    
                    line_text = ""
                current_attrs = attrs
            
            line_text += cell.char
        
        # Insert remaining text for this line
        if line_text.strip():  # Only if there's actual content
            tag_name = f"debug_tag_{tag_counter}"
            tag_counter += 1
            
            if current_attrs:
                fg_color, bg_color, bold, underline = current_attrs
                print(f"  Creating final tag {tag_name}: fg={fg_color}, bg={bg_color}, bold={bold}")
                
                font_config = ('Courier New', 12)
                if bold:
                    font_config = ('Courier New', 12, 'bold')
                
                print(f"  Configuring final tag with foreground={fg_color}, background={bg_color}")
                text_widget.tag_configure(
                    tag_name,
                    foreground=fg_color,
                    background=bg_color,
                    font=font_config
                )
                
                print(f"  Inserting final text '{line_text.rstrip()}' with tag {tag_name}")
                text_widget.insert(tk.END, line_text, tag_name)
                
                # Verify tag was applied
                tag_ranges = text_widget.tag_ranges(tag_name)
                print(f"  Final tag ranges: {tag_ranges}")
        
        # Add newline except for last line
        if y < len(emulator.screen) - 1:
            text_widget.insert(tk.END, '\n')
    
    # Disable editing
    text_widget.configure(state=tk.DISABLED)
    
    # Test: Add a manual red tag to compare
    text_widget.configure(state=tk.NORMAL)
    text_widget.insert(tk.END, "\n\nManual red test: ")
    text_widget.insert(tk.END, "This should be red", "manual_red")
    text_widget.tag_configure("manual_red", foreground="#CD0000")
    text_widget.configure(state=tk.DISABLED)
    
    # Instructions
    instruction_label = tk.Label(
        root, 
        text="Check console for debug output.\nYou should see 'Red' in red color and manual red test.\nIf manual red works but 'Red' doesn't, there's an issue with tag application.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("\nWindow opened with debug render!")
    print("Check if:")
    print("1. 'Red' appears in red color")
    print("2. 'Manual red test' appears in red color")
    print("3. Console shows tag creation and configuration")
    
    # Run the GUI
    root.mainloop()
    
    print("Debug complete!")

if __name__ == "__main__":
    debug_render_method()
