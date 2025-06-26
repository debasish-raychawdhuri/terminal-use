#!/usr/bin/env python3
"""
Compare color methods to find the exact difference.
"""

import tkinter as tk
from tkinter import scrolledtext

def compare_color_methods():
    """Compare different ways of applying the same color."""
    
    print("=== Comparing Color Methods ===")
    
    root = tk.Tk()
    root.title("Color Method Comparison")
    root.geometry("800x500")
    
    text_widget = scrolledtext.ScrolledText(
        root,
        wrap=tk.NONE,
        font=('Courier New', 12),
        bg='black',
        fg='white'
    )
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Method 1: Simple tag (this worked in your test)
    text_widget.insert(tk.END, "Method 1 - Simple red tag: ")
    text_widget.insert(tk.END, "RED TEXT\n", "simple_red")
    text_widget.tag_configure("simple_red", foreground="#CD0000")
    
    # Method 2: Terminal emulator style (exact same color)
    text_widget.insert(tk.END, "Method 2 - Emulator style: ")
    text_widget.insert(tk.END, "RED TEXT\n", "emulator_red")
    text_widget.tag_configure(
        "emulator_red",
        foreground="#CD0000",
        background="black",
        font=('Courier New', 12)
    )
    
    # Method 3: Different red values
    text_widget.insert(tk.END, "Method 3 - Bright red: ")
    text_widget.insert(tk.END, "RED TEXT\n", "bright_red")
    text_widget.tag_configure("bright_red", foreground="#FF0000")
    
    text_widget.insert(tk.END, "Method 4 - Dark red: ")
    text_widget.insert(tk.END, "RED TEXT\n", "dark_red")
    text_widget.tag_configure("dark_red", foreground="#800000")
    
    text_widget.insert(tk.END, "Method 5 - Named color: ")
    text_widget.insert(tk.END, "RED TEXT\n", "named_red")
    text_widget.tag_configure("named_red", foreground="red")
    
    # Method 6: Test if background interferes
    text_widget.insert(tk.END, "Method 6 - No background: ")
    text_widget.insert(tk.END, "RED TEXT\n", "no_bg_red")
    text_widget.tag_configure(
        "no_bg_red",
        foreground="#CD0000",
        font=('Courier New', 12)
    )
    
    # Method 7: Test if font interferes
    text_widget.insert(tk.END, "Method 7 - No font spec: ")
    text_widget.insert(tk.END, "RED TEXT\n", "no_font_red")
    text_widget.tag_configure(
        "no_font_red",
        foreground="#CD0000",
        background="black"
    )
    
    # Method 8: Test state issues
    text_widget.configure(state=tk.DISABLED)
    text_widget.configure(state=tk.NORMAL)
    text_widget.insert(tk.END, "Method 8 - After state change: ")
    text_widget.insert(tk.END, "RED TEXT\n", "state_red")
    text_widget.tag_configure("state_red", foreground="#CD0000")
    
    # Instructions
    instruction_label = tk.Label(
        root, 
        text="Compare all the red text methods above.\nWhich ones show RED color and which ones show WHITE?\nThis will help identify the exact issue.\nClose window when done.",
        bg='lightgray',
        font=('Arial', 10)
    )
    instruction_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    print("Window opened with different color methods!")
    print("Check which methods show RED color vs WHITE color:")
    print("1. Simple red tag")
    print("2. Emulator style (with background and font)")
    print("3. Bright red (#FF0000)")
    print("4. Dark red (#800000)")
    print("5. Named color ('red')")
    print("6. No background specified")
    print("7. No font specified")
    print("8. After state change")
    
    # Run the GUI
    root.mainloop()
    
    print("Comparison complete!")

if __name__ == "__main__":
    compare_color_methods()
