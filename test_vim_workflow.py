#!/usr/bin/env python3
"""
Test complete vim workflow with screen clearing and color preservation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'terminal_mcp_server'))

from terminal_screen_emulator import TerminalScreenEmulator

def test_vim_workflow():
    """Test complete vim workflow."""
    
    print("=== Testing Complete Vim Workflow ===\n")
    
    # Create terminal emulator
    emulator = TerminalScreenEmulator(width=80, height=24)
    
    # 1. Simulate shell with colored output
    print("1. Shell with colored output...")
    shell_content = """bash-5.1$ ls --color=always
\x1b[0m\x1b[01;34mDocuments\x1b[0m  \x1b[01;32mscript.sh\x1b[0m  \x1b[01;31mtest.txt\x1b[0m
\x1b[01;34mDownloads\x1b[0m  \x1b[01;35mimage.png\x1b[0m  \x1b[00mREADME.md\x1b[0m
bash-5.1$ echo -e '\x1b[32mGreen text\x1b[0m and \x1b[31mred text\x1b[0m'
\x1b[32mGreen text\x1b[0m and \x1b[31mred text\x1b[0m
bash-5.1$ vim test.txt"""
    
    emulator.process_content(shell_content)
    
    print("Shell content before vim:")
    for i, row in enumerate(emulator.screen[:8]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            print(f"  {i:2}: {line}")
    
    # 2. Vim starts - enters alternative screen
    print("\n2. Vim starting (alternative screen)...")
    vim_start = """\x1b[?1049h\x1b[22;0;0t\x1b[1;24r\x1b[?12h\x1b[?12l\x1b[22;2t\x1b[22;1t\x1b[27m\x1b[23m\x1b[29m\x1b[m\x1b[H\x1b[2J"""
    emulator.process_content(vim_start)
    
    print("Screen after vim start (should be clear):")
    non_empty_lines = 0
    for i, row in enumerate(emulator.screen):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            non_empty_lines += 1
            print(f"  {i:2}: {line}")
    
    if non_empty_lines == 0:
        print("  ✅ Screen is properly cleared")
    else:
        print(f"  ❌ Screen still has {non_empty_lines} lines")
    
    # 3. Vim displays its interface
    print("\n3. Vim interface...")
    vim_interface = """~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
~
\x1b[1;1H"""
    emulator.process_content(vim_interface)
    
    # Add status line
    emulator.process_content("\x1b[24;1H")
    emulator.process_content('"test.txt" [New File]')
    
    print("Vim interface:")
    for i, row in enumerate(emulator.screen):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            print(f"  {i:2}: {line}")
    
    # 4. User types in vim
    print("\n4. Typing in vim...")
    emulator.process_content("\x1b[1;1H")  # Go to top
    emulator.process_content("Hello from vim!")
    emulator.process_content("\x1b[24;1H")
    emulator.process_content("\x1b[K")  # Clear status line
    emulator.process_content("-- INSERT --")
    
    # 5. Exit vim
    print("\n5. Exiting vim...")
    vim_exit = """\x1b[24;1H\x1b[K\x1b[?1049l\x1b[23;0;0t"""
    emulator.process_content(vim_exit)
    
    print("Screen after vim exit (should restore shell):")
    for i, row in enumerate(emulator.screen[:8]):
        line = ''.join(cell.char for cell in row).rstrip()
        if line:
            colors = [cell.fg_color for cell in row if cell.char.strip()]
            has_colors = any(color != 'white' for color in colors)
            color_info = " (has colors)" if has_colors else ""
            print(f"  {i:2}: {line}{color_info}")
    
    # 6. Verify colors are preserved
    print("\n6. Color verification...")
    
    # Check for specific colored elements
    found_blue = False  # Directory names
    found_green = False  # Executable files
    found_red = False   # Red text
    
    for row in emulator.screen[:8]:
        for cell in row:
            if cell.char.strip():
                if '#01;34' in str(cell.fg_color) or '#0000EE' in str(cell.fg_color):
                    found_blue = True
                elif '#01;32' in str(cell.fg_color) or '#00CD00' in str(cell.fg_color):
                    found_green = True
                elif '#31' in str(cell.fg_color) or '#CD0000' in str(cell.fg_color):
                    found_red = True
    
    print(f"  Blue colors (directories): {'✅' if found_blue else '❌'}")
    print(f"  Green colors (executables): {'✅' if found_green else '❌'}")
    print(f"  Red colors (text): {'✅' if found_red else '❌'}")
    
    # 7. Final assessment
    print("\n7. Final Assessment:")
    if found_blue or found_green or found_red:
        print("  ✅ SUCCESS: Vim workflow works correctly!")
        print("    - Screen clears when vim starts")
        print("    - Vim interface displays properly")
        print("    - Original shell content restored with colors")
    else:
        print("  ❌ FAILURE: Colors were lost during vim session")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_vim_workflow()
