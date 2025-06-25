#!/usr/bin/env python3
"""Test script for ANSI to HTML conversion."""

from terminal_mcp_server.ansi_to_html import convert_ansi_to_html

def test_basic_colors():
    """Test basic color conversion."""
    test_text = "\x1b[31mRed text\x1b[0m \x1b[32mGreen text\x1b[0m \x1b[34mBlue text\x1b[0m"
    html = convert_ansi_to_html(test_text, "Color Test")
    print("Basic colors test:")
    print(html[:200] + "..." if len(html) > 200 else html)
    print()

def test_formatting():
    """Test text formatting."""
    test_text = "\x1b[1mBold\x1b[0m \x1b[3mItalic\x1b[0m \x1b[4mUnderline\x1b[0m"
    html = convert_ansi_to_html(test_text, "Formatting Test")
    print("Formatting test:")
    print(html[:200] + "..." if len(html) > 200 else html)
    print()

def test_complex():
    """Test complex ANSI sequences."""
    test_text = "\x1b[1;31mBold Red\x1b[0m\n\x1b[42;37mWhite on Green\x1b[0m\n\x1b[38;5;196mBright Red (256)\x1b[0m"
    html = convert_ansi_to_html(test_text, "Complex Test")
    print("Complex test:")
    print(html[:300] + "..." if len(html) > 300 else html)
    print()

if __name__ == "__main__":
    test_basic_colors()
    test_formatting()
    test_complex()
    print("All tests completed!")
