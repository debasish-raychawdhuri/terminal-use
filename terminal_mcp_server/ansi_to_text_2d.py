"""ANSI escape sequence to plain text converter with proper 2D terminal screen handling."""

import re
from typing import List, Optional


class Terminal2DTextRenderer:
    """Renders ANSI escape sequences to plain text with proper 2D terminal layout."""
    
    # ANSI escape sequence patterns
    CSI_PATTERN = re.compile(r'\x1b\[([0-9;?]*)([a-zA-Z])')
    OSC_PATTERN = re.compile(r'\x1b\]([^\x07\x1b]*)\x07')
    SIMPLE_ESCAPE_PATTERN = re.compile(r'\x1b[^[]')
    
    def __init__(self, width: int = 120, height: int = 40):
        """Initialize the terminal renderer."""
        self.width = width
        self.height = height
        self.reset_terminal()
    
    def reset_terminal(self):
        """Reset the terminal state."""
        # Create 2D grid of characters (no color info needed)
        self.screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Current cursor position
        self.cursor_row = 0
        self.cursor_col = 0
    
    def handle_cursor_position(self, params: List[int]):
        """Handle cursor positioning (CUP) sequences."""
        if not params:
            row, col = 1, 1
        elif len(params) == 1:
            row, col = params[0], 1
        else:
            row, col = params[0], params[1]
        
        # Convert to 0-based indexing and clamp to screen bounds
        self.cursor_row = max(0, min(self.height - 1, row - 1))
        self.cursor_col = max(0, min(self.width - 1, col - 1))
    
    def put_char(self, char: str):
        """Put a character at the current cursor position."""
        if 0 <= self.cursor_row < self.height and 0 <= self.cursor_col < self.width:
            self.screen[self.cursor_row][self.cursor_col] = char
            
            # Advance cursor
            self.cursor_col += 1
            if self.cursor_col >= self.width:
                self.cursor_col = 0
                self.cursor_row += 1
    
    def process_text(self, text: str):
        """Process ANSI text and populate the terminal screen (text only)."""
        i = 0
        while i < len(text):
            # Look for ANSI escape sequences
            csi_match = self.CSI_PATTERN.match(text, i)
            if csi_match:
                # Process CSI sequence
                params_str, command = csi_match.groups()
                
                # Parse parameters
                params = []
                if params_str:
                    try:
                        # Handle parameters with ? prefix
                        clean_params = params_str.lstrip('?')
                        if clean_params:
                            params = [int(p) if p else 0 for p in clean_params.split(';')]
                    except ValueError:
                        params = []
                
                # Handle cursor movement commands (ignore color commands)
                if command in ['H', 'f']:
                    # CUP - Cursor Position
                    self.handle_cursor_position(params)
                elif command == 'A':
                    # CUU - Cursor Up
                    count = params[0] if params else 1
                    self.cursor_row = max(0, self.cursor_row - count)
                elif command == 'B':
                    # CUD - Cursor Down
                    count = params[0] if params else 1
                    self.cursor_row = min(self.height - 1, self.cursor_row + count)
                elif command == 'C':
                    # CUF - Cursor Forward
                    count = params[0] if params else 1
                    self.cursor_col = min(self.width - 1, self.cursor_col + count)
                elif command == 'D':
                    # CUB - Cursor Back
                    count = params[0] if params else 1
                    self.cursor_col = max(0, self.cursor_col - count)
                # Ignore SGR (color) and other sequences
                
                i = csi_match.end()
                continue
            
            # Look for OSC sequences (title setting, etc.)
            osc_match = self.OSC_PATTERN.match(text, i)
            if osc_match:
                # Skip OSC sequences
                i = osc_match.end()
                continue
            
            # Look for simple escape sequences
            simple_match = self.SIMPLE_ESCAPE_PATTERN.match(text, i)
            if simple_match:
                # Skip simple escape sequences
                i = simple_match.end()
                continue
            
            # Regular character
            char = text[i]
            if char == '\r':
                # Carriage return - move to beginning of line
                self.cursor_col = 0
            elif char == '\n':
                # Line feed - move to next line
                self.cursor_row += 1
                if self.cursor_row >= self.height:
                    self.cursor_row = self.height - 1
            elif char == '\t':
                # Tab - advance to next tab stop (every 8 columns)
                next_tab = ((self.cursor_col // 8) + 1) * 8
                self.cursor_col = min(self.width - 1, next_tab)
            elif ord(char) >= 32:  # Printable character
                self.put_char(char)
            
            i += 1
    
    def render_to_text(self) -> str:
        """Render the terminal screen to plain text."""
        lines = []
        
        for row in self.screen:
            # Convert row to string and strip trailing spaces
            line = ''.join(row).rstrip()
            lines.append(line)
        
        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines)


def convert_ansi_to_text_2d(text: str, width: int = 120, height: int = 40) -> str:
    """Convert ANSI text to plain text with proper 2D terminal layout."""
    renderer = Terminal2DTextRenderer(width, height)
    renderer.process_text(text)
    return renderer.render_to_text()


def convert_ansi_to_text_linear(text: str) -> str:
    """Convert ANSI text to plain text with linear processing (for simple commands)."""
    # Remove all ANSI escape sequences
    ansi_pattern = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
    clean_text = ansi_pattern.sub('', text)
    
    # Clean up other escape sequences
    osc_pattern = re.compile(r'\x1b\]([^\x07\x1b]*)\x07')
    clean_text = osc_pattern.sub('', clean_text)
    
    simple_escape_pattern = re.compile(r'\x1b[^[]')
    clean_text = simple_escape_pattern.sub('', clean_text)
    
    return clean_text
