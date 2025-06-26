#!/usr/bin/env python3
"""
Test the proper terminal screen emulator.
"""

import tkinter as tk
from terminal_mcp_server.terminal_screen_emulator import TerminalScreenEmulator

def test_terminal_emulator():
    """Test the terminal screen emulator directly."""
    print("Testing terminal screen emulator...")
    
    # Create tkinter window
    root = tk.Tk()
    root.title("Terminal Emulator Test")
    root.geometry("1000x700")
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
    
    # Test content with positioning and colors
    test_content = """Normal text at start
\x1b[31mRed text\x1b[0m
\x1b[10;20HPositioned text at row 10, col 20
\x1b[32mGreen text continues\x1b[0m
\x1b[1;1H\x1b[2J\x1b[34mScreen cleared, blue text at top\x1b[0m
\x1b[5;10H\x1b[1;33mBold yellow at 5,10\x1b[0m
\x1b[15;30H\x1b[41mRed background\x1b[0m
\x1b[20;1HBottom text with \x1b[35mmagenta\x1b[0m color"""
    
    print("Processing terminal content with positioning and colors...")
    emulator.process_content(test_content)
    
    print("Rendering to tkinter...")
    emulator.render_to_tkinter(text_widget)
    
    print("Check the window - you should see:")
    print("✓ Properly positioned text (not scattered)")
    print("✓ Colors preserved (red, green, blue, yellow, magenta)")
    print("✓ Screen clearing working correctly")
    print("✓ Text at specific positions")
    
    # Add button to test TUI-like updates
    def simulate_tui_update():
        # Simulate a TUI app updating the screen
        tui_content = """\x1b[2J\x1b[1;1H┌─────────────────────────────────────┐
│           CALCULATOR                │
├─────────────────────────────────────┤
│                              \x1b[32m123\x1b[0m │
│                                     │
│ \x1b[44m 7 \x1b[0m \x1b[44m 8 \x1b[0m \x1b[44m 9 \x1b[0m \x1b[43m + \x1b[0m               │
│ \x1b[44m 4 \x1b[0m \x1b[44m 5 \x1b[0m \x1b[44m 6 \x1b[0m \x1b[43m - \x1b[0m               │
│ \x1b[44m 1 \x1b[0m \x1b[44m 2 \x1b[0m \x1b[44m 3 \x1b[0m \x1b[43m * \x1b[0m               │
│ \x1b[44m 0 \x1b[0m     \x1b[42m = \x1b[0m \x1b[43m / \x1b[0m               │
└─────────────────────────────────────┘"""
        
        emulator.process_content(tui_content)
        emulator.render_to_tkinter(text_widget)
    
    update_button = tk.Button(root, text="Simulate TUI Calculator", command=simulate_tui_update)
    update_button.pack(pady=5)
    
    print("Click 'Simulate TUI Calculator' to see TUI-style interface")
    print("Close window when done testing.")
    root.mainloop()

if __name__ == "__main__":
    test_terminal_emulator()
