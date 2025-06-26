#!/usr/bin/env python3
"""
Test if tkinter color tags work at all.
"""

import tkinter as tk
from tkinter import scrolledtext

def test_tkinter_tags():
    """Test basic tkinter color functionality."""
    
    print("=== Testing Basic Tkinter Color Tags ===")
    
    root = tk.Tk()
    root.title("Tkinter Color Tag Test")
    root.geometry("600x400")
    
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 12),
        bg='black',
        fg='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Test 1: Basic color tags
    print("Testing basic color tags...")
    text_widget.insert(tk.END, "This should be WHITE (default)\n")
    text_widget.insert(tk.END, "This should be RED\n", "red_tag")
    text_widget.insert(tk.END, "This should be GREEN\n", "green_tag")
    text_widget.insert(tk.END, "This should be BLUE\n", "blue_tag")
    text_widget.insert(tk.END, "This should be YELLOW\n", "yellow_tag")
    
    # Configure the tags with exact colors from terminal emulator
    text_widget.tag_configure("red_tag", foreground="#CD0000")
    text_widget.tag_configure("green_tag", foreground="#00CD00")
    text_widget.tag_configure("blue_tag", foreground="#0000EE")
    text_widget.tag_configure("yellow_tag", foreground="#CDCD00")
    
    # Test 2: Same approach as terminal emulator
    text_widget.insert(tk.END, "\n--- Terminal Emulator Style ---\n")
    
    # Simulate what the terminal emulator does
    tag_counter = 0
    
    # Red text
    tag_name = f"color_tag_{tag_counter}"
    tag_counter += 1
    text_widget.tag_configure(
        tag_name,
        foreground="#CD0000",  # Same as COLORS[31]
        background="black",
        font=('Courier New', 12)
    )
    text_widget.insert(tk.END, "Emulator style RED\n", tag_name)
    
    # Green text
    tag_name = f"color_tag_{tag_counter}"
    tag_counter += 1
    text_widget.tag_configure(
        tag_name,
        foreground="#00CD00",  # Same as COLORS[32]
        background="black",
        font=('Courier New', 12)
    )
    text_widget.insert(tk.END, "Emulator style GREEN\n", tag_name)
    
    # Blue text
    tag_name = f"color_tag_{tag_counter}"
    tag_counter += 1
    text_widget.tag_configure(
        tag_name,
        foreground="#0000EE",  # Same as COLORS[34]
        background="black",
        font=('Courier New', 12)
    )
    text_widget.insert(tk.END, "Emulator style BLUE\n", tag_name)
    
    # Test 3: Debug tag configuration
    text_widget.insert(tk.END, "\n--- Debug Info ---\n")
    text_widget.insert(tk.END, f"Red color code: #CD0000\n")
    text_widget.insert(tk.END, f"Green color code: #00CD00\n")
    text_widget.insert(tk.END, f"Blue color code: #0000EE\n")
    
    # Instructions
    instruction_label = tk.Label(
        root, 
        text="Check if you can see COLORED text above.\nIf all text is white, tkinter color tags are not working.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("Window opened. Check if you can see:")
    print("- RED colored text")
    print("- GREEN colored text")
    print("- BLUE colored text")
    print("- YELLOW colored text")
    print()
    print("If you can't see colors, there's a tkinter configuration issue.")
    
    # Run the GUI
    root.mainloop()
    
    print("Test complete!")

if __name__ == "__main__":
    test_tkinter_tags()
