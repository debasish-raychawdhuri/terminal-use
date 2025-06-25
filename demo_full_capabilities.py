#!/usr/bin/env python3
"""Demonstrate the full capabilities of the HTML rendering."""

from terminal_mcp_server.ansi_to_html import convert_ansi_to_html

def create_comprehensive_demo():
    """Create a comprehensive demo of all ANSI features."""
    
    demo_content = """
🎨 COMPREHENSIVE ANSI TO HTML DEMO 🎨

=== BASIC COLORS ===
\x1b[30mBlack\x1b[0m \x1b[31mRed\x1b[0m \x1b[32mGreen\x1b[0m \x1b[33mYellow\x1b[0m \x1b[34mBlue\x1b[0m \x1b[35mMagenta\x1b[0m \x1b[36mCyan\x1b[0m \x1b[37mWhite\x1b[0m

=== BRIGHT COLORS ===
\x1b[90mBright Black\x1b[0m \x1b[91mBright Red\x1b[0m \x1b[92mBright Green\x1b[0m \x1b[93mBright Yellow\x1b[0m \x1b[94mBright Blue\x1b[0m \x1b[95mBright Magenta\x1b[0m \x1b[96mBright Cyan\x1b[0m \x1b[97mBright White\x1b[0m

=== TEXT FORMATTING ===
\x1b[1mBold Text\x1b[0m
\x1b[2mDim Text\x1b[0m
\x1b[3mItalic Text\x1b[0m
\x1b[4mUnderlined Text\x1b[0m
\x1b[5mBlinking Text\x1b[0m
\x1b[7mReverse Video\x1b[0m
\x1b[9mStrikethrough Text\x1b[0m

=== COMBINED FORMATTING ===
\x1b[1;31mBold Red\x1b[0m
\x1b[3;32mItalic Green\x1b[0m
\x1b[4;33mUnderlined Yellow\x1b[0m
\x1b[1;4;35mBold Underlined Magenta\x1b[0m
\x1b[1;3;4;36mBold Italic Underlined Cyan\x1b[0m

=== BACKGROUND COLORS ===
\x1b[40mBlack BG\x1b[0m \x1b[41mRed BG\x1b[0m \x1b[42mGreen BG\x1b[0m \x1b[43mYellow BG\x1b[0m \x1b[44mBlue BG\x1b[0m \x1b[45mMagenta BG\x1b[0m \x1b[46mCyan BG\x1b[0m \x1b[47mWhite BG\x1b[0m

=== BRIGHT BACKGROUND COLORS ===
\x1b[100mBright Black BG\x1b[0m \x1b[101mBright Red BG\x1b[0m \x1b[102mBright Green BG\x1b[0m \x1b[103mBright Yellow BG\x1b[0m \x1b[104mBright Blue BG\x1b[0m \x1b[105mBright Magenta BG\x1b[0m \x1b[106mBright Cyan BG\x1b[0m \x1b[107mBright White BG\x1b[0m

=== 256-COLOR PALETTE ===
\x1b[38;5;196mBright Red (196)\x1b[0m \x1b[38;5;46mBright Green (46)\x1b[0m \x1b[38;5;21mBright Blue (21)\x1b[0m \x1b[38;5;226mBright Yellow (226)\x1b[0m \x1b[38;5;201mBright Magenta (201)\x1b[0m \x1b[38;5;51mBright Cyan (51)\x1b[0m

=== RGB COLORS ===
\x1b[38;2;255;0;0mPure Red RGB\x1b[0m
\x1b[38;2;0;255;0mPure Green RGB\x1b[0m
\x1b[38;2;0;0;255mPure Blue RGB\x1b[0m
\x1b[38;2;255;165;0mOrange RGB\x1b[0m
\x1b[38;2;128;0;128mPurple RGB\x1b[0m
\x1b[38;2;255;192;203mPink RGB\x1b[0m

=== COMPLEX COMBINATIONS ===
\x1b[1;38;2;255;215;0;48;2;128;0;128mGold on Purple\x1b[0m
\x1b[3;4;38;5;196;48;5;46mItalic Underlined Red on Green\x1b[0m
\x1b[7;1;33mReverse Bold Yellow\x1b[0m

=== GRADIENTS AND PATTERNS ===
\x1b[38;5;196m█\x1b[38;5;202m█\x1b[38;5;208m█\x1b[38;5;214m█\x1b[38;5;220m█\x1b[38;5;226m█\x1b[0m Red to Yellow Gradient
\x1b[38;5;21m█\x1b[38;5;27m█\x1b[38;5;33m█\x1b[38;5;39m█\x1b[38;5;45m█\x1b[38;5;51m█\x1b[0m Blue to Cyan Gradient

=== TERMINAL ART ===
\x1b[31m  ♥♥♥♥♥♥♥\x1b[0m
\x1b[31m♥♥♥♥♥♥♥♥♥\x1b[0m
\x1b[31m♥♥♥♥♥♥♥♥♥\x1b[0m
\x1b[31m ♥♥♥♥♥♥♥\x1b[0m
\x1b[31m  ♥♥♥♥♥\x1b[0m
\x1b[31m   ♥♥♥\x1b[0m
\x1b[31m    ♥\x1b[0m

=== PROGRESS BARS ===
\x1b[42m████████████████████\x1b[0m\x1b[41m          \x1b[0m 67%
\x1b[46m███████████████\x1b[0m\x1b[40m               \x1b[0m 50%
\x1b[43m██████████\x1b[0m\x1b[47m                    \x1b[0m 33%

=== TABLE WITH COLORS ===
\x1b[1;37m┌─────────────┬─────────────┬─────────────┐\x1b[0m
\x1b[1;37m│\x1b[0m \x1b[1;32mName\x1b[0m        \x1b[1;37m│\x1b[0m \x1b[1;33mStatus\x1b[0m      \x1b[1;37m│\x1b[0m \x1b[1;34mValue\x1b[0m       \x1b[1;37m│\x1b[0m
\x1b[1;37m├─────────────┼─────────────┼─────────────┤\x1b[0m
\x1b[1;37m│\x1b[0m Server      \x1b[1;37m│\x1b[0m \x1b[32mRunning\x1b[0m     \x1b[1;37m│\x1b[0m \x1b[36m100%\x1b[0m        \x1b[1;37m│\x1b[0m
\x1b[1;37m│\x1b[0m Database    \x1b[1;37m│\x1b[0m \x1b[31mError\x1b[0m       \x1b[1;37m│\x1b[0m \x1b[35m0%\x1b[0m          \x1b[1;37m│\x1b[0m
\x1b[1;37m│\x1b[0m Cache       \x1b[1;37m│\x1b[0m \x1b[33mWarning\x1b[0m     \x1b[1;37m│\x1b[0m \x1b[93m75%\x1b[0m         \x1b[1;37m│\x1b[0m
\x1b[1;37m└─────────────┴─────────────┴─────────────┘\x1b[0m

=== LOG LEVELS ===
\x1b[90m[DEBUG]\x1b[0m   Debug message in gray
\x1b[36m[INFO]\x1b[0m    Info message in cyan
\x1b[33m[WARN]\x1b[0m    Warning message in yellow
\x1b[31m[ERROR]\x1b[0m   Error message in red
\x1b[1;31m[FATAL]\x1b[0m   Fatal message in bold red

=== SYNTAX HIGHLIGHTING SIMULATION ===
\x1b[35mfunction\x1b[0m \x1b[32mhelloWorld\x1b[0m\x1b[37m(\x1b[0m\x1b[33mname\x1b[0m\x1b[37m)\x1b[0m \x1b[37m{\x1b[0m
    \x1b[34mconsole\x1b[0m\x1b[37m.\x1b[0m\x1b[32mlog\x1b[0m\x1b[37m(\x1b[0m\x1b[31m"Hello, "\x1b[0m \x1b[37m+\x1b[0m \x1b[33mname\x1b[0m \x1b[37m+\x1b[0m \x1b[31m"!"\x1b[0m\x1b[37m);\x1b[0m
\x1b[37m}\x1b[0m

🎉 END OF DEMO - ALL ANSI FEATURES RENDERED! 🎉
""".strip()
    
    # Convert to HTML
    html_content = convert_ansi_to_html(demo_content, "Complete ANSI Feature Demo")
    
    # Save to file
    with open("complete_ansi_demo.html", "w") as f:
        f.write(html_content)
    
    print("✅ Complete ANSI demo created!")
    print(f"HTML length: {len(html_content)} characters")
    print("Saved to complete_ansi_demo.html")
    print("\nFeatures demonstrated:")
    print("- 16 standard colors + 8 bright colors")
    print("- Bold, italic, underline, strikethrough formatting")
    print("- Background colors (standard + bright)")
    print("- 256-color palette")
    print("- RGB colors")
    print("- Complex combinations")
    print("- Terminal art and graphics")
    print("- Tables and progress bars")
    print("- Syntax highlighting simulation")
    print("- No truncation - complete output preserved!")

if __name__ == "__main__":
    create_comprehensive_demo()
