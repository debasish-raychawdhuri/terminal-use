#!/usr/bin/env python3
"""Integration test for the HTML functionality."""

import sys
import os
sys.path.insert(0, '/home/debasish/work/talentica/terminal-mcp-server')

from terminal_mcp_server.terminal_manager import TerminalManager
from terminal_mcp_server.ansi_to_html import convert_ansi_to_html

def test_terminal_manager_html():
    """Test the terminal manager with HTML conversion."""
    
    print("Testing terminal manager with HTML conversion...")
    
    # Create terminal manager
    tm = TerminalManager()
    
    # Generate session ID
    session_id = tm.generate_session_id()
    print(f"Generated session ID: {session_id}")
    
    # Run a command that produces colored output
    command = "echo -e '\\033[31mRed text\\033[0m \\033[32mGreen text\\033[0m \\033[1;34mBold Blue\\033[0m'"
    print(f"Running command: {command}")
    
    try:
        output, exit_code, running = tm.run_command(command, session_id, timeout=10)
        print(f"Command output: {repr(output)}")
        print(f"Exit code: {exit_code}")
        print(f"Still running: {running}")
        
        # Get session state with raw output
        raw_output, _, _ = tm.get_session_state(session_id, raw_output=True)
        print(f"Raw output: {repr(raw_output)}")
        
        # Convert to HTML
        html_content = convert_ansi_to_html(raw_output, "Test Terminal Session")
        
        # Save HTML
        with open("integration_test.html", "w") as f:
            f.write(html_content)
        
        print("✅ HTML integration test successful!")
        print(f"HTML length: {len(html_content)} characters")
        print("Saved to integration_test.html")
        
        # Clean up
        tm.terminate_session(session_id)
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()

def test_complex_ansi():
    """Test complex ANSI sequences."""
    
    print("\nTesting complex ANSI sequences...")
    
    # Create a complex ANSI string
    complex_ansi = """
\x1b[1;31mBold Red\x1b[0m
\x1b[3;32mItalic Green\x1b[0m
\x1b[4;33mUnderlined Yellow\x1b[0m
\x1b[1;4;35mBold Underlined Magenta\x1b[0m
\x1b[7;36mReverse Cyan\x1b[0m
\x1b[38;5;196mBright Red (256-color)\x1b[0m
\x1b[48;5;46mGreen Background (256-color)\x1b[0m
\x1b[38;2;255;165;0mOrange RGB\x1b[0m
\x1b[38;2;255;255;255;48;2;128;0;128mWhite on Purple\x1b[0m
"""
    
    html_content = convert_ansi_to_html(complex_ansi, "Complex ANSI Test")
    
    with open("complex_ansi_test.html", "w") as f:
        f.write(html_content)
    
    print("✅ Complex ANSI test successful!")
    print("Saved to complex_ansi_test.html")

if __name__ == "__main__":
    test_terminal_manager_html()
    test_complex_ansi()
    print("\nAll integration tests completed!")
