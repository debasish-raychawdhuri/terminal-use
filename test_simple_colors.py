#!/usr/bin/env python3
"""
Test the simple color display directly.
"""

import tkinter as tk
from terminal_mcp_server.simple_color_display import SimpleColorDisplay

def test_simple_colors():
    """Test the simple color display."""
    print("Testing simple color display...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Simple Color Test")
    root.geometry("800x400")
    root.configure(bg='black')
    
    # Create text widget
    text_widget = tk.Text(
        root,
        bg='black',
        fg='white',
        font=('Courier New', 12),
        wrap=tk.NONE
    )
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create simple color display
    color_display = SimpleColorDisplay(text_widget)
    
    # Test content with colors and escape sequences
    test_content = """Normal white text
\x1b[31mThis should be RED\x1b[0m
\x1b[32mThis should be GREEN\x1b[0m
\x1b[34mThis should be BLUE\x1b[0m
\x1b[1;33mThis should be BOLD YELLOW\x1b[0m
\x1b[35mThis should be MAGENTA\x1b[0m
\x1b[36mThis should be CYAN\x1b[0m
\x1b]697;OSCUnlock=test\x07This should appear (OSC filtered)
\x1b[91mThis should be BRIGHT RED\x1b[0m
\x1b[92mThis should be BRIGHT GREEN\x1b[0m
Back to normal white text"""
    
    print("Displaying content with simple color renderer...")
    color_display.display_with_colors(test_content)
    
    print("Check the window - you should see:")
    print("✓ RED, GREEN, BLUE, BOLD YELLOW, MAGENTA, CYAN colors")
    print("✓ BRIGHT RED and BRIGHT GREEN colors")
    print("✓ Normal text without escape sequences")
    print("✗ NO literal \\x1b sequences visible")
    
    print("Close the window when done.")
    root.mainloop()

if __name__ == "__main__":
    test_simple_colors()
