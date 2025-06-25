#!/usr/bin/env python3
"""Test script to generate HTML files for visual inspection."""

import os
from terminal_mcp_server.ansi_to_html import convert_ansi_to_html

def create_test_html():
    """Create test HTML files."""
    
    # Test 1: Basic colors
    test1 = """
\x1b[31mRed text\x1b[0m
\x1b[32mGreen text\x1b[0m
\x1b[33mYellow text\x1b[0m
\x1b[34mBlue text\x1b[0m
\x1b[35mMagenta text\x1b[0m
\x1b[36mCyan text\x1b[0m
\x1b[37mWhite text\x1b[0m
"""
    
    # Test 2: Formatting
    test2 = """
\x1b[1mBold text\x1b[0m
\x1b[3mItalic text\x1b[0m
\x1b[4mUnderlined text\x1b[0m
\x1b[9mStrikethrough text\x1b[0m
\x1b[1;4mBold and underlined\x1b[0m
"""
    
    # Test 3: Background colors
    test3 = """
\x1b[41mRed background\x1b[0m
\x1b[42mGreen background\x1b[0m
\x1b[43mYellow background\x1b[0m
\x1b[44mBlue background\x1b[0m
\x1b[45mMagenta background\x1b[0m
\x1b[46mCyan background\x1b[0m
\x1b[47mWhite background\x1b[0m
"""
    
    # Test 4: Complex combinations
    test4 = """
\x1b[1;31;42mBold red text on green background\x1b[0m
\x1b[4;33;44mUnderlined yellow text on blue background\x1b[0m
\x1b[3;36;41mItalic cyan text on red background\x1b[0m
\x1b[7mReverse video\x1b[0m
"""
    
    # Test 5: 256-color support
    test5 = """
\x1b[38;5;196mBright red (256-color)\x1b[0m
\x1b[38;5;46mBright green (256-color)\x1b[0m
\x1b[38;5;21mBright blue (256-color)\x1b[0m
\x1b[48;5;226mYellow background (256-color)\x1b[0m
\x1b[38;5;196;48;5;226mRed on yellow (256-color)\x1b[0m
"""
    
    # Test 6: RGB colors
    test6 = """
\x1b[38;2;255;100;50mRGB orange text\x1b[0m
\x1b[48;2;50;150;255mRGB blue background\x1b[0m
\x1b[38;2;255;255;255;48;2;128;0;128mWhite on purple\x1b[0m
"""
    
    tests = [
        (test1, "basic_colors.html", "Basic Colors"),
        (test2, "formatting.html", "Text Formatting"),
        (test3, "backgrounds.html", "Background Colors"),
        (test4, "complex.html", "Complex Combinations"),
        (test5, "256_colors.html", "256-Color Support"),
        (test6, "rgb_colors.html", "RGB Colors"),
    ]
    
    for test_content, filename, title in tests:
        html = convert_ansi_to_html(test_content.strip(), title)
        with open(filename, 'w') as f:
            f.write(html)
        print(f"Created {filename}")
    
    # Create a comprehensive test
    comprehensive = "\n".join([test[0].strip() for test in tests])
    html = convert_ansi_to_html(comprehensive, "Comprehensive ANSI Test")
    with open("comprehensive_test.html", 'w') as f:
        f.write(html)
    print("Created comprehensive_test.html")

if __name__ == "__main__":
    create_test_html()
    print("\nHTML test files created. Open them in a browser to verify rendering.")
