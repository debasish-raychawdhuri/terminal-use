"""
Terminal screen buffer for capturing and interpreting terminal output.
"""

import re
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class TerminalScreenBuffer:
    """A buffer that maintains the current state of a terminal screen."""
    
    def __init__(self, rows: int = 40, cols: int = 100):
        """Initialize the screen buffer.
        
        Args:
            rows: Number of rows in the terminal
            cols: Number of columns in the terminal
        """
        self.rows = rows
        self.cols = cols
        self.cursor_row = 0
        self.cursor_col = 0
        
        # Initialize screen with empty spaces
        self.screen = [[' ' for _ in range(cols)] for _ in range(rows)]
        
        # Raw output buffer for debugging
        self.raw_buffer = ""
        
    def process_data(self, data: str) -> None:
        """Process incoming terminal data and update screen buffer.
        
        Args:
            data: Raw terminal data containing text and ANSI escape sequences
        """
        self.raw_buffer += data
        
        # Keep raw buffer reasonable size
        if len(self.raw_buffer) > 10000:
            self.raw_buffer = self.raw_buffer[-8000:]
        
        i = 0
        while i < len(data):
            char = data[i]
            
            if char == '\x1b':  # ESC - start of escape sequence
                i = self._process_escape_sequence(data, i)
            elif char == '\r':  # Carriage return
                self.cursor_col = 0
                i += 1
            elif char == '\n':  # Line feed
                self.cursor_row += 1
                if self.cursor_row >= self.rows:
                    self._scroll_up()
                    self.cursor_row = self.rows - 1
                i += 1
            elif char == '\t':  # Tab
                # Move to next tab stop (every 8 characters)
                self.cursor_col = ((self.cursor_col // 8) + 1) * 8
                if self.cursor_col >= self.cols:
                    self.cursor_col = self.cols - 1
                i += 1
            elif char == '\b':  # Backspace
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                i += 1
            elif ord(char) >= 32:  # Printable character
                self._put_char(char)
                i += 1
            else:
                # Skip other control characters
                i += 1
    
    def _process_escape_sequence(self, data: str, start: int) -> int:
        """Process an ANSI escape sequence.
        
        Args:
            data: The data string
            start: Starting position of the escape sequence
            
        Returns:
            New position after processing the sequence
        """
        if start + 1 >= len(data):
            return start + 1
        
        if data[start + 1] == '[':  # CSI sequence
            return self._process_csi_sequence(data, start)
        elif data[start + 1] == ']':  # OSC sequence
            return self._process_osc_sequence(data, start)
        else:
            # Other escape sequences - skip for now
            return start + 2
    
    def _process_csi_sequence(self, data: str, start: int) -> int:
        """Process a CSI (Control Sequence Introducer) sequence.
        
        Args:
            data: The data string
            start: Starting position of the CSI sequence
            
        Returns:
            New position after processing the sequence
        """
        # Find the end of the CSI sequence
        i = start + 2  # Skip ESC[
        while i < len(data) and data[i] in '0123456789;?':
            i += 1
        
        if i >= len(data):
            return len(data)
        
        command = data[i]
        params_str = data[start + 2:i]
        
        # Parse parameters
        if params_str:
            try:
                params = [int(p) if p else 0 for p in params_str.split(';')]
            except ValueError:
                params = []
        else:
            params = []
        
        # Process common CSI commands
        if command == 'H':  # Cursor position
            row = (params[0] - 1) if params else 0
            col = (params[1] - 1) if len(params) > 1 else 0
            self.cursor_row = max(0, min(row, self.rows - 1))
            self.cursor_col = max(0, min(col, self.cols - 1))
        elif command == 'A':  # Cursor up
            n = params[0] if params else 1
            self.cursor_row = max(0, self.cursor_row - n)
        elif command == 'B':  # Cursor down
            n = params[0] if params else 1
            self.cursor_row = min(self.rows - 1, self.cursor_row + n)
        elif command == 'C':  # Cursor right
            n = params[0] if params else 1
            self.cursor_col = min(self.cols - 1, self.cursor_col + n)
        elif command == 'D':  # Cursor left
            n = params[0] if params else 1
            self.cursor_col = max(0, self.cursor_col - n)
        elif command == 'J':  # Erase display
            if not params or params[0] == 0:  # Clear from cursor to end
                self._clear_from_cursor_to_end()
            elif params[0] == 1:  # Clear from start to cursor
                self._clear_from_start_to_cursor()
            elif params[0] == 2:  # Clear entire screen
                self._clear_screen()
        elif command == 'K':  # Erase line
            if not params or params[0] == 0:  # Clear from cursor to end of line
                self._clear_line_from_cursor()
            elif params[0] == 1:  # Clear from start of line to cursor
                self._clear_line_to_cursor()
            elif params[0] == 2:  # Clear entire line
                self._clear_entire_line()
        elif command == 'm':  # SGR (colors, etc.) - ignore for now
            pass
        
        return i + 1
    
    def _process_osc_sequence(self, data: str, start: int) -> int:
        """Process an OSC (Operating System Command) sequence.
        
        Args:
            data: The data string
            start: Starting position of the OSC sequence
            
        Returns:
            New position after processing the sequence
        """
        # Find the end of the OSC sequence (terminated by BEL or ST)
        i = start + 2  # Skip ESC]
        while i < len(data):
            if data[i] == '\x07':  # BEL
                return i + 1
            elif i + 1 < len(data) and data[i:i+2] == '\x1b\\':  # ST
                return i + 2
            i += 1
        
        return len(data)
    
    def _put_char(self, char: str) -> None:
        """Put a character at the current cursor position.
        
        Args:
            char: Character to put
        """
        if self.cursor_row < self.rows and self.cursor_col < self.cols:
            self.screen[self.cursor_row][self.cursor_col] = char
            self.cursor_col += 1
            
            if self.cursor_col >= self.cols:
                self.cursor_col = 0
                self.cursor_row += 1
                if self.cursor_row >= self.rows:
                    self._scroll_up()
                    self.cursor_row = self.rows - 1
    
    def _scroll_up(self) -> None:
        """Scroll the screen up by one line."""
        for i in range(self.rows - 1):
            self.screen[i] = self.screen[i + 1][:]
        self.screen[self.rows - 1] = [' ' for _ in range(self.cols)]
    
    def _clear_screen(self) -> None:
        """Clear the entire screen."""
        self.screen = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.cursor_row = 0
        self.cursor_col = 0
    
    def _clear_from_cursor_to_end(self) -> None:
        """Clear from cursor to end of screen."""
        # Clear rest of current line
        for col in range(self.cursor_col, self.cols):
            self.screen[self.cursor_row][col] = ' '
        
        # Clear remaining lines
        for row in range(self.cursor_row + 1, self.rows):
            for col in range(self.cols):
                self.screen[row][col] = ' '
    
    def _clear_from_start_to_cursor(self) -> None:
        """Clear from start of screen to cursor."""
        # Clear previous lines
        for row in range(self.cursor_row):
            for col in range(self.cols):
                self.screen[row][col] = ' '
        
        # Clear current line up to cursor
        for col in range(self.cursor_col + 1):
            self.screen[self.cursor_row][col] = ' '
    
    def _clear_line_from_cursor(self) -> None:
        """Clear from cursor to end of current line."""
        for col in range(self.cursor_col, self.cols):
            self.screen[self.cursor_row][col] = ' '
    
    def _clear_line_to_cursor(self) -> None:
        """Clear from start of line to cursor."""
        for col in range(self.cursor_col + 1):
            self.screen[self.cursor_row][col] = ' '
    
    def _clear_entire_line(self) -> None:
        """Clear the entire current line."""
        for col in range(self.cols):
            self.screen[self.cursor_row][col] = ' '
    
    def get_screen_content(self) -> str:
        """Get the current screen content as a string.
        
        Returns:
            String representation of the screen
        """
        lines = []
        for row in self.screen:
            line = ''.join(row).rstrip()
            lines.append(line)
        
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get the current cursor position.
        
        Returns:
            Tuple of (row, col)
        """
        return (self.cursor_row, self.cursor_col)
    
    def get_raw_buffer(self) -> str:
        """Get the raw buffer for debugging.
        
        Returns:
            Raw terminal data
        """
        return self.raw_buffer
