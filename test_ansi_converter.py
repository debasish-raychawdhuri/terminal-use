#!/usr/bin/env python3
"""
Test the ANSI converter directly to see if colors work.
"""

import tkinter as tk
from terminal_mcp_server.ansi_to_tkinter import ANSIToTkinter
import time

def test_ansi_converter():
    """Test the ANSI converter directly."""
    print("Testing ANSI converter...")
    
    # Create a simple tkinter window
    root = tk.Tk()
    root.title("ANSI Color Test")
    root.geometry("800x400")
    root.configure(bg='black')
    
    # Create text widget
    text_widget = tk.Text(
        root,
        bg='black',
        fg='white',
        font=('Courier New', 12),
        wrap=tk.NONE,
        state=tk.NORMAL
    )
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create ANSI converter
    converter = ANSIToTkinter(text_widget)
    
    # Test content with various colors
    test_content = """Normal white text
\x1b[31mThis should be RED\x1b[0m
\x1b[32mThis should be GREEN\x1b[0m
\x1b[34mThis should be BLUE\x1b[0m
\x1b[1;33mThis should be BOLD YELLOW\x1b[0m
\x1b[35mThis should be MAGENTA\x1b[0m
\x1b[36mThis should be CYAN\x1b[0m
\x1b[91mThis should be BRIGHT RED\x1b[0m
\x1b[92mThis should be BRIGHT GREEN\x1b[0m
Back to normal white text
\x1b[41mThis should have RED BACKGROUND\x1b[0m
\x1b[42mThis should have GREEN BACKGROUND\x1b[0m
Final normal text"""
    
    print("Inserting test content with colors...")
    converter.clear_and_insert_with_colors(test_content)
    
    print("If colors are working, you should see:")
    print("- RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN colored text")
    print("- BRIGHT RED and BRIGHT GREEN text")
    print("- RED and GREEN background colors")
    
    # Add a button to test updates
    def update_content():
        new_content = test_content + f"\n\x1b[93mUpdated at {time.strftime('%H:%M:%S')}\x1b[0m"
        converter.clear_and_insert_with_colors(new_content)
    
    update_button = tk.Button(root, text="Update Content", command=update_content)
    update_button.pack(pady=5)
    
    print("Window should now show colored text. Close window to continue.")
    root.mainloop()

if __name__ == "__main__":
    test_ansi_converter()
