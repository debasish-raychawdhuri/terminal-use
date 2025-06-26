"""
Proper terminal screen emulator that handles TUI applications correctly.
"""

import re
import tkinter as tk
from typing import List, Tuple, Dict, Optional


class TerminalCell:
    """Represents a single character cell in the terminal."""
    
    def __init__(self, char: str = ' ', fg_color: str = 'white', bg_color: str = 'black', 
                 bold: bool = False, underline: bool = False):
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.bold = bold
        self.underline = underline
    
    def __str__(self):
        return self.char


class TerminalScreenEmulator:
    """Emulates a terminal screen with proper cursor positioning and colors."""
    
    # ANSI color mapping
    COLORS = {
        30: '#000000', 31: '#CD0000', 32: '#00CD00', 33: '#CDCD00',
        34: '#0000EE', 35: '#CD00CD', 36: '#00CDCD', 37: '#E5E5E5',
        90: '#7F7F7F', 91: '#FF0000', 92: '#00FF00', 93: '#FFFF00',
        94: '#5C5CFF', 95: '#FF00FF', 96: '#00FFFF', 97: '#FFFFFF'
    }
    
    BG_COLORS = {
        40: '#000000', 41: '#CD0000', 42: '#00CD00', 43: '#CDCD00',
        44: '#0000EE', 45: '#CD00CD', 46: '#00CDCD', 47: '#E5E5E5',
        100: '#7F7F7F', 101: '#FF0000', 102: '#00FF00', 103: '#FFFF00',
        104: '#5C5CFF', 105: '#FF00FF', 106: '#00FFFF', 107: '#FFFFFF'
    }
    
    def __init__(self, width: int = 80, height: int = 24):
        """Initialize the terminal screen emulator.
        
        Args:
            width: Screen width in characters
            height: Screen height in characters
        """
        self.width = width
        self.height = height
        self.cursor_x = 0
        self.cursor_y = 0
        
        # Current text attributes
        self.current_fg = 'white'
        self.current_bg = 'black'
        self.current_bold = False
        self.current_underline = False
        
        # Screen buffer - 2D array of TerminalCell objects
        self.screen = [[TerminalCell() for _ in range(width)] for _ in range(height)]
        
        # Alternative screen buffer support
        self.alt_screen = None
        self.in_alt_screen = False
        self.saved_cursor = (0, 0)
    
    def process_content(self, content: str):
        """Process terminal content with proper ANSI handling.
        
        Args:
            content: Raw terminal content with ANSI sequences
        """
        # More comprehensive ANSI sequence pattern
        # This pattern matches:
        # - CSI sequences: \x1b[...letter (including parameters and private modes)
        # - OSC sequences: \x1b]...(\x07 or \x1b\\) 
        # - Other escape sequences
        pattern = r'(\x1b\[[?!>]?[0-9;:<=>?]*[a-zA-Z@`]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()#%*+].|\x1b[DEHMNOVWXZ78]|\x1b=|\x1b>|\x1b\][^\\x07\\x1b]*\\x07)'
        
        # Split content into parts
        parts = re.split(pattern, content)
        
        for part in parts:
            if not part:  # Skip empty parts
                continue
            elif part.startswith('\x1b['):
                # CSI sequence - handle colors, cursor movement, etc.
                self._handle_csi_sequence(part)
            elif part.startswith('\x1b]'):
                # OSC sequence - ignore (window titles, etc.)
                self._handle_osc_sequence(part)
            elif part.startswith('\x1b'):
                # Other escape sequences - ignore
                pass
            else:
                # Regular text - insert into screen buffer
                self._insert_text(part)
    
    def _handle_csi_sequence(self, sequence: str):
        """Handle CSI (Control Sequence Introducer) sequences.
        
        Args:
            sequence: The CSI sequence (e.g., '\x1b[31m')
        """
        if sequence.endswith('m'):
            # SGR (Select Graphic Rendition) - colors and formatting
            params = sequence[2:-1]  # Remove \x1b[ and m
            self._handle_sgr(params)
        elif sequence.endswith('H') or sequence.endswith('f'):
            # Cursor position
            params = sequence[2:-1]
            self._handle_cursor_position(params)
        elif sequence.endswith('A'):
            # Cursor up
            params = sequence[2:-1]
            count = int(params) if params else 1
            self.cursor_y = max(0, self.cursor_y - count)
        elif sequence.endswith('B'):
            # Cursor down
            params = sequence[2:-1]
            count = int(params) if params else 1
            self.cursor_y = min(self.height - 1, self.cursor_y + count)
        elif sequence.endswith('C'):
            # Cursor right
            params = sequence[2:-1]
            count = int(params) if params else 1
            self.cursor_x = min(self.width - 1, self.cursor_x + count)
        elif sequence.endswith('D'):
            # Cursor left
            params = sequence[2:-1]
            count = int(params) if params else 1
            self.cursor_x = max(0, self.cursor_x - count)
        elif sequence.endswith('J'):
            # Clear screen
            params = sequence[2:-1]
            self._handle_clear_screen(params)
        elif sequence.endswith('K'):
            # Clear line
            params = sequence[2:-1]
            self._handle_clear_line(params)
        elif sequence.endswith('h') and '?' in sequence:
            # Set mode
            params = sequence[2:-1]
            self._handle_set_mode(params)
        elif sequence.endswith('l') and '?' in sequence:
            # Reset mode
            params = sequence[2:-1]
            self._handle_reset_mode(params)
        elif sequence.endswith('s'):
            # Save cursor position
            self.saved_cursor = (self.cursor_x, self.cursor_y)
        elif sequence.endswith('u'):
            # Restore cursor position
            self.cursor_x, self.cursor_y = self.saved_cursor
        elif sequence.endswith('G'):
            # Cursor horizontal absolute
            params = sequence[2:-1]
            col = int(params) - 1 if params else 0
            self.cursor_x = max(0, min(self.width - 1, col))
        elif sequence.endswith('d'):
            # Line position absolute
            params = sequence[2:-1]
            row = int(params) - 1 if params else 0
            self.cursor_y = max(0, min(self.height - 1, row))
        elif sequence.endswith('@'):
            # Insert character
            params = sequence[2:-1]
            count = int(params) if params else 1
            # Shift characters to the right
            for _ in range(count):
                if self.cursor_x < self.width - 1:
                    for x in range(self.width - 1, self.cursor_x, -1):
                        self.screen[self.cursor_y][x] = self.screen[self.cursor_y][x - 1]
                    self.screen[self.cursor_y][self.cursor_x] = TerminalCell()
        elif sequence.endswith('P'):
            # Delete character
            params = sequence[2:-1]
            count = int(params) if params else 1
            # Shift characters to the left
            for _ in range(count):
                for x in range(self.cursor_x, self.width - 1):
                    self.screen[self.cursor_y][x] = self.screen[self.cursor_y][x + 1]
                self.screen[self.cursor_y][self.width - 1] = TerminalCell()
        # Ignore any other CSI sequences we don't handle
    
    def _handle_sgr(self, params: str):
        """Handle SGR (color/formatting) parameters.
        
        Args:
            params: SGR parameters (e.g., "1;31;42")
        """
        if not params:
            params = '0'
        
        codes = [int(p) for p in params.split(';') if p.isdigit()]
        
        for code in codes:
            if code == 0:  # Reset
                self.current_fg = 'white'
                self.current_bg = 'black'
                self.current_bold = False
                self.current_underline = False
            elif code == 1:  # Bold
                self.current_bold = True
            elif code == 4:  # Underline
                self.current_underline = True
            elif code == 22:  # Normal intensity
                self.current_bold = False
            elif code == 24:  # Not underlined
                self.current_underline = False
            elif code in self.COLORS:  # Foreground colors
                self.current_fg = self.COLORS[code]
            elif code in self.BG_COLORS:  # Background colors
                self.current_bg = self.BG_COLORS[code]
    
    def _handle_cursor_position(self, params: str):
        """Handle cursor positioning.
        
        Args:
            params: Position parameters (e.g., "10;20")
        """
        if not params:
            self.cursor_x = 0
            self.cursor_y = 0
        else:
            parts = params.split(';')
            if len(parts) >= 2:
                row = int(parts[0]) - 1 if parts[0] else 0
                col = int(parts[1]) - 1 if parts[1] else 0
                self.cursor_y = max(0, min(self.height - 1, row))
                self.cursor_x = max(0, min(self.width - 1, col))
    
    def _handle_clear_screen(self, params: str):
        """Handle screen clearing.
        
        Args:
            params: Clear parameters
        """
        if not params or params == '0':
            # Clear from cursor to end of screen
            for y in range(self.cursor_y, self.height):
                start_x = self.cursor_x if y == self.cursor_y else 0
                for x in range(start_x, self.width):
                    self.screen[y][x] = TerminalCell()
        elif params == '1':
            # Clear from beginning of screen to cursor
            for y in range(0, self.cursor_y + 1):
                end_x = self.cursor_x if y == self.cursor_y else self.width - 1
                for x in range(0, end_x + 1):
                    self.screen[y][x] = TerminalCell()
        elif params == '2':
            # Clear entire screen and reset cursor to top-left
            self.screen = [[TerminalCell() for _ in range(self.width)] for _ in range(self.height)]
            self.cursor_x = 0
            self.cursor_y = 0
    
    def _handle_clear_line(self, params: str):
        """Handle line clearing.
        
        Args:
            params: Clear parameters
        """
        if not params or params == '0':
            # Clear from cursor to end of line
            for x in range(self.cursor_x, self.width):
                self.screen[self.cursor_y][x] = TerminalCell()
        elif params == '1':
            # Clear from beginning of line to cursor
            for x in range(0, self.cursor_x + 1):
                self.screen[self.cursor_y][x] = TerminalCell()
        elif params == '2':
            # Clear entire line
            for x in range(self.width):
                self.screen[self.cursor_y][x] = TerminalCell()
    
    def _handle_set_mode(self, params: str):
        """Handle mode setting.
        
        Args:
            params: Mode parameters
        """
        if params == '?1049':
            # Enter alternative screen buffer
            if not self.in_alt_screen:
                # Save current screen with deep copy to preserve colors
                self.alt_screen = []
                for row in self.screen:
                    new_row = []
                    for cell in row:
                        new_cell = TerminalCell(cell.char, cell.fg_color, cell.bg_color, cell.bold, cell.underline)
                        new_row.append(new_cell)
                    self.alt_screen.append(new_row)
                
                # Clear the screen for vim
                self.screen = [[TerminalCell() for _ in range(self.width)] for _ in range(self.height)]
                self.cursor_x = 0
                self.cursor_y = 0
                self.in_alt_screen = True
        elif params == '?25':
            # Show cursor (ignore for display purposes)
            pass
        elif params == '?1000' or params == '?1002' or params == '?1006':
            # Mouse tracking modes (ignore)
            pass
        elif params == '?47':
            # Alternative screen buffer (older version)
            if not self.in_alt_screen:
                # Save current screen with deep copy to preserve colors
                self.alt_screen = []
                for row in self.screen:
                    new_row = []
                    for cell in row:
                        new_cell = TerminalCell(cell.char, cell.fg_color, cell.bg_color, cell.bold, cell.underline)
                        new_row.append(new_cell)
                    self.alt_screen.append(new_row)
                
                # Clear the screen
                self.screen = [[TerminalCell() for _ in range(self.width)] for _ in range(self.height)]
                self.cursor_x = 0
                self.cursor_y = 0
                self.in_alt_screen = True
    
    def _handle_reset_mode(self, params: str):
        """Handle mode resetting.
        
        Args:
            params: Mode parameters
        """
        if params == '?1049':
            # Exit alternative screen buffer
            if self.in_alt_screen and self.alt_screen:
                # Restore the saved screen with all colors preserved
                self.screen = self.alt_screen
                self.alt_screen = None
                self.in_alt_screen = False
                # Don't reset cursor position - let it stay where vim left it
        elif params == '?25':
            # Hide cursor (ignore for display purposes)
            pass
        elif params == '?1000' or params == '?1002' or params == '?1006':
            # Mouse tracking modes (ignore)
            pass
        elif params == '?47':
            # Exit alternative screen buffer (older version)
            if self.in_alt_screen and self.alt_screen:
                # Restore the saved screen with all colors preserved
                self.screen = self.alt_screen
                self.alt_screen = None
                self.in_alt_screen = False
    
    def _handle_osc_sequence(self, sequence: str):
        """Handle OSC (Operating System Command) sequences.
        
        Args:
            sequence: The OSC sequence
        """
        # Ignore OSC sequences (window titles, etc.)
        pass
    
    def _insert_text(self, text: str):
        """Insert text at the current cursor position.
        
        Args:
            text: Text to insert
        """
        # Final cleanup: remove any remaining escape sequences that slipped through
        # This catches sequences like \x1b= or other single-character escapes
        clean_text = re.sub(r'\x1b[^[].*?[a-zA-Z@`~]|\x1b.', '', text)
        
        for char in clean_text:
            if char == '\n':
                self.cursor_y = min(self.height - 1, self.cursor_y + 1)
                self.cursor_x = 0
            elif char == '\r':
                self.cursor_x = 0
            elif char == '\t':
                # Tab to next 8-character boundary
                self.cursor_x = min(self.width - 1, ((self.cursor_x // 8) + 1) * 8)
            elif ord(char) >= 32:  # Printable character
                if self.cursor_y < self.height and self.cursor_x < self.width:
                    self.screen[self.cursor_y][self.cursor_x] = TerminalCell(
                        char, self.current_fg, self.current_bg, 
                        self.current_bold, self.current_underline
                    )
                    self.cursor_x += 1
                    if self.cursor_x >= self.width:
                        self.cursor_x = 0
                        self.cursor_y = min(self.height - 1, self.cursor_y + 1)
    
    def render_to_tkinter(self, text_widget: tk.Text):
        """Render the screen buffer to a tkinter Text widget.
        
        Args:
            text_widget: The tkinter Text widget to render to
        """
        # Enable editing
        text_widget.configure(state=tk.NORMAL)
        
        # Clear existing content
        text_widget.delete(1.0, tk.END)
        
        # Render each line
        for y, row in enumerate(self.screen):
            line_text = ""
            current_attrs = None
            tag_counter = 0
            
            for x, cell in enumerate(row):
                # Check if attributes changed
                attrs = (cell.fg_color, cell.bg_color, cell.bold, cell.underline)
                if attrs != current_attrs:
                    # Insert accumulated text with previous attributes
                    if line_text and current_attrs:
                        tag_name = f"tag_{tag_counter}"
                        tag_counter += 1
                        self._configure_tag(text_widget, tag_name, current_attrs)
                        text_widget.insert(tk.END, line_text, tag_name)
                        line_text = ""
                    current_attrs = attrs
                
                line_text += cell.char
            
            # Insert remaining text for this line
            if line_text:
                # Always apply color tags, even for "default" colors
                # This ensures colors are properly displayed
                tag_name = f"tag_{tag_counter}"
                tag_counter += 1
                self._configure_tag(text_widget, tag_name, current_attrs)
                text_widget.insert(tk.END, line_text, tag_name)
            
            # Add newline except for last line
            if y < len(self.screen) - 1:
                text_widget.insert(tk.END, '\n')
        
        # Disable editing
        text_widget.configure(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        text_widget.see(tk.END)
    
    def _configure_tag(self, text_widget: tk.Text, tag_name: str, attrs: Tuple):
        """Configure a text tag with the given attributes.
        
        Args:
            text_widget: The text widget
            tag_name: Name of the tag
            attrs: Tuple of (fg_color, bg_color, bold, underline)
        """
        fg_color, bg_color, bold, underline = attrs
        
        font_config = ('Courier New', 10)
        if bold and underline:
            font_config = ('Courier New', 10, 'bold', 'underline')
        elif bold:
            font_config = ('Courier New', 10, 'bold')
        elif underline:
            font_config = ('Courier New', 10, 'underline')
        
        text_widget.tag_configure(
            tag_name,
            foreground=fg_color,
            background=bg_color,
            font=font_config
        )
