"""Terminal manager for handling terminal sessions."""

import logging
import os
import re
import signal
import subprocess
import time
import uuid
from typing import Dict, List, Optional, Tuple, Union

import pexpect

from terminal_mcp_server.terminal_emulator import TerminalEmulatorSession, detect_terminal_emulator

logger = logging.getLogger(__name__)

# Regular expression to match ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi_escape_sequences(text: str) -> str:
    """Strip ANSI escape sequences from text.
    
    Args:
        text: The text to strip
        
    Returns:
        The text with ANSI escape sequences removed
    """
    return ANSI_ESCAPE_PATTERN.sub('', text)


class TerminalSession:
    """Class representing a terminal session."""

    def __init__(self, command: str, timeout: int = 30, term_type: str = "xterm-256color", 
                 dimensions: Tuple[int, int] = (36, 120), preserve_ansi: bool = True):
        """Initialize a terminal session.
        
        Args:
            command: The command to run
            timeout: Timeout in seconds
            term_type: Terminal type to emulate
            dimensions: Terminal dimensions (rows, columns)
            preserve_ansi: Whether to preserve ANSI escape sequences in output
        """
        self.command = command
        self.timeout = timeout
        self.process = None
        self.output_buffer = ""
        self.raw_output_buffer = ""
        self.exit_code = None
        self.start_time = time.time()
        self.preserve_ansi = preserve_ansi
        self.term_type = term_type
        self.dimensions = dimensions
        
        # Start the process
        try:
            env = os.environ.copy()
            env["TERM"] = self.term_type
            
            self.process = pexpect.spawn(
                "/bin/bash", ["-c", command], 
                encoding="utf-8", 
                timeout=timeout,
                dimensions=dimensions,
                env=env
            )
            logger.info(f"Started process with command: {command}")
            
            # Try to get initial output immediately
            self._read_output()
            
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            raise
    
    def _read_output(self) -> str:
        """Read available output from the process without blocking.
        
        Returns:
            New raw output that was read
        """
        if not self.is_running():
            return ""
            
        try:
            # Try to read any new output without blocking
            self.process.expect("__UNLIKELY_PATTERN__", timeout=0.1)
        except pexpect.TIMEOUT:
            # This is expected, we just want to capture output
            pass
        except pexpect.EOF:
            # Process ended
            self.exit_code = self.process.exitstatus
        
        # Get the output since last read
        new_raw_output = self.process.before or ""
        self.raw_output_buffer += new_raw_output
        
        # Process the output based on preference
        if not self.preserve_ansi:
            new_output = strip_ansi_escape_sequences(new_raw_output)
            self.output_buffer += new_output
            
        return new_raw_output
    
    def send_input(self, input_text: str) -> str:
        """Send input to the terminal.
        
        Args:
            input_text: The input to send
            
        Returns:
            The output after sending the input
        """
        if not self.is_running():
            raise RuntimeError("Process is not running")
        
        # Send the input
        self.process.sendline(input_text)
        
        # Wait for output and capture it
        try:
            # Use a pattern that's unlikely to be in the output to force timeout
            # This allows us to capture whatever output is available
            self.process.expect("__UNLIKELY_PATTERN__", timeout=1)
        except pexpect.TIMEOUT:
            # This is expected, we just want to capture output
            pass
        except pexpect.EOF:
            # Process ended
            self.exit_code = self.process.exitstatus
        
        # Get the output since last read
        new_raw_output = self.process.before
        self.raw_output_buffer += new_raw_output
        
        # Process the output based on preference
        if self.preserve_ansi:
            new_output = new_raw_output
        else:
            new_output = strip_ansi_escape_sequences(new_raw_output)
        
        self.output_buffer += new_output
        
        return new_output
    
    def get_output(self, raw: bool = None) -> str:
        """Get the current output from the terminal.
        
        Args:
            raw: Override the preserve_ansi setting if not None
            
        Returns:
            The current output
        """
        # Read any new output
        self._read_output()
        
        # Determine whether to return raw output
        if raw is None:
            use_raw = self.preserve_ansi
        else:
            use_raw = raw
            
        return self.raw_output_buffer if use_raw else self.output_buffer
    
    def is_running(self) -> bool:
        """Check if the process is still running.
        
        Returns:
            True if the process is running, False otherwise
        """
        if self.process is None:
            return False
        
        return self.process.isalive()
    
    def terminate(self) -> None:
        """Terminate the process."""
        if not self.is_running():
            return
        
        try:
            # Try graceful termination first
            self.process.terminate(force=False)
            time.sleep(0.5)
            
            # If still running, force kill
            if self.is_running():
                self.process.terminate(force=True)
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
            # As a last resort
            try:
                if self.process.pid:
                    os.kill(self.process.pid, signal.SIGKILL)
            except Exception:
                pass
        
        # Capture any final output
        self._read_output()
        
        # Set exit code if not already set
        if self.exit_code is None and self.process.exitstatus is not None:
            self.exit_code = self.process.exitstatus


class TerminalManager:
    """Manager for terminal sessions."""

    def __init__(self):
        """Initialize the terminal manager."""
        self.sessions: Dict[str, Union[TerminalSession, TerminalEmulatorSession]] = {}
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID.
        
        Returns:
            A unique session ID
        """
        return str(uuid.uuid4())
    
    def run_command(
        self, command: str, session_id: str, timeout: int = 30,
        use_terminal_emulator: bool = False, terminal_emulator: Optional[str] = None
    ) -> Tuple[str, Optional[int], bool]:
        """Run a command in a terminal.
        
        Args:
            command: The command to run
            session_id: The session ID
            timeout: Timeout in seconds
            use_terminal_emulator: Whether to use a terminal emulator
            terminal_emulator: Terminal emulator to use (if None, auto-detect)
            
        Returns:
            Tuple of (output, exit_code, running)
        """
        # Check if session already exists
        if session_id in self.sessions:
            # Terminate existing session
            self.terminate_session(session_id)
        
        # Create new session
        if use_terminal_emulator:
            # Use terminal emulator for TUI applications
            if terminal_emulator is None:
                terminal_emulator = detect_terminal_emulator()
            
            logger.info(f"Using terminal emulator: {terminal_emulator}")
            session = TerminalEmulatorSession(command, timeout, emulator=terminal_emulator, 
                                             dimensions=(40, 100))  # Set to 40 rows, 100 columns
        else:
            # Use regular terminal session
            session = TerminalSession(command, timeout)
        
        self.sessions[session_id] = session
        
        # For simple commands, wait for completion or a reasonable timeout
        # This ensures we capture the output before returning
        is_simple_command = not use_terminal_emulator
        wait_time = 0
        max_wait = 2  # Maximum seconds to wait for simple commands
        
        while is_simple_command and session.is_running() and wait_time < max_wait:
            time.sleep(0.1)
            wait_time += 0.1
            
            # Check if we have output already
            output = session.get_output()
            if output and len(output) > 0:
                # If we have output and it's been at least 0.5 seconds, we can return
                if wait_time >= 0.5:
                    break
        
        # Get final output
        output = session.get_output()
        exit_code = getattr(session, 'exit_code', None)
        running = session.is_running()
        
        return output, exit_code, running
    
    def send_input(self, session_id: str, input_text: str) -> Tuple[str, Optional[int], bool]:
        """Send input to a terminal session.
        
        Args:
            session_id: The session ID
            input_text: The input to send
            
        Returns:
            Tuple of (output, exit_code, running)
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Send input and get output
        output = session.send_input(input_text)
        exit_code = getattr(session, 'exit_code', None)
        running = session.is_running()
        
        return output, exit_code, running
    
    def get_session_state(self, session_id: str, raw_output: bool = None) -> Tuple[str, Optional[int], bool]:
        """Get the current state of a terminal session.
        
        Args:
            session_id: The session ID
            raw_output: Whether to return raw output with ANSI escape sequences
            
        Returns:
            Tuple of (output, exit_code, running)
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        try:
            # Get current state with timeout protection
            if hasattr(session, 'get_output') and callable(getattr(session, 'get_output')):
                if raw_output is not None and 'raw' in session.get_output.__code__.co_varnames:
                    output = session.get_output(raw=raw_output)
                else:
                    output = session.get_output()
            else:
                output = getattr(session, 'output_buffer', '')
            
            exit_code = getattr(session, 'exit_code', None)
            running = session.is_running() if hasattr(session, 'is_running') else False
            
            return output, exit_code, running
            
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            # Return safe defaults if there's an error
            return f"Error getting session state: {str(e)}", None, False
    
    def terminate_session(self, session_id: str) -> None:
        """Terminate a terminal session.
        
        Args:
            session_id: The session ID
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        session.terminate()
        
        # Remove from sessions
        del self.sessions[session_id]
    
    def list_sessions(self) -> List[str]:
        """List all active terminal sessions.
        
        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists.
        
        Args:
            session_id: The session ID to check
            
        Returns:
            True if the session exists, False otherwise
        """
        return session_id in self.sessions
    
    def get_session_output(self, session_id: str, raw_output: bool = False) -> Optional[Dict[str, any]]:
        """Get the output from a terminal session for live display.
        
        Args:
            session_id: The session ID
            raw_output: Whether to return raw output with ANSI sequences
            
        Returns:
            Dict with session information or None if session doesn't exist
        """
        if session_id not in self.sessions:
            return None
            
        try:
            session = self.sessions[session_id]
            
            # For TUI applications, we want the current screen state, not history
            # For regular shell sessions, we want the full history
            if hasattr(session, 'get_screen_content') and self._is_tui_active(session):
                # TUI app is active - show current screen state
                output = session.get_screen_content()
            elif hasattr(session, 'get_output'):
                # Regular shell session - show full history
                output = session.get_output(raw=raw_output)
            elif hasattr(session, 'output_buffer'):
                # Fallback to output buffer
                output = getattr(session, 'output_buffer', '')
            else:
                # Last resort - use screen content
                output = session.get_screen_content() if hasattr(session, 'get_screen_content') else ''
            
            return {
                'output': output,
                'running': session.is_running() if hasattr(session, 'is_running') else False,
                'exit_code': getattr(session, 'exit_code', None)
            }
            
        except Exception as e:
            logger.error(f"Error getting session output: {e}")
            return None
    
    def _is_tui_active(self, session) -> bool:
        """Detect if a TUI application is currently active in the session.
        
        Args:
            session: The terminal session
            
        Returns:
            True if a TUI app is detected, False otherwise
        """
        try:
            # Check if we have recent output that indicates TUI mode
            if hasattr(session, 'output_buffer'):
                recent_output = session.output_buffer[-3000:]  # Last 3000 chars
                
                # Look for TUI indicators in recent output
                tui_indicators = [
                    '\x1b[?1049h',  # Alternative screen buffer (vim, less, etc.)
                    '\x1b[?47h',    # Alternative screen buffer (older)
                    '\x1b[2J\x1b[H', # Clear screen + home cursor (common TUI pattern)
                    '\x1b[?25l',    # Hide cursor (common in TUI apps)
                    '\x1b[?1000h',  # Mouse tracking (TUI apps)
                    '\x1b[?1002h',  # Mouse tracking (TUI apps)
                    '\x1b[?1006h',  # Mouse tracking (TUI apps)
                    '\x1b[2J',      # Clear screen (calculator apps)
                    '\x1b[H\x1b[2J', # Home + clear (calculator apps)
                ]
                
                # Count TUI indicators
                tui_score = 0
                for indicator in tui_indicators:
                    if indicator in recent_output:
                        tui_score += 1
                
                # If we have multiple TUI indicators, likely in TUI mode
                if tui_score >= 1:  # Lowered threshold for calculator apps
                    return True
                
                # Check for high frequency of escape sequences (TUI apps generate many)
                escape_count = recent_output.count('\x1b[')
                if escape_count > 20:  # High escape sequence density indicates TUI
                    return True
                
                # Also check for vim-specific patterns
                vim_patterns = [
                    b'VIM - Vi IMproved',
                    b'-- INSERT --',
                    b'-- VISUAL --',
                    b'~\r\n~\r\n~\r\n',  # Multiple tilde lines (vim empty buffer)
                ]
                
                # Check for calculator-specific patterns
                calc_patterns = [
                    b'calculator',
                    b'Calculator',
                    b'[0-9]+\.[0-9]+',  # Decimal numbers (calculator display)
                    b'[+\-*/=]',        # Math operators
                ]
                
                recent_bytes = recent_output.encode('utf-8', errors='ignore')
                for pattern in vim_patterns + calc_patterns:
                    if pattern in recent_bytes:
                        return True
            
            # Also check if screen buffer has been recently updated with structured content
            if hasattr(session, 'screen_buffer'):
                # If screen buffer has content that looks like a TUI interface
                screen_content = session.screen_buffer.get_screen_content()
                if screen_content and len(screen_content.strip()) > 100:
                    # Check for TUI-like patterns in screen content
                    lines = screen_content.split('\n')
                    if len(lines) > 10:  # TUI apps usually have many lines
                        # Look for patterns like vim's tilde lines or structured layout
                        tilde_lines = sum(1 for line in lines if line.strip() == '~')
                        if tilde_lines > 5:  # Vim shows many ~ lines
                            return True
                        
                        # Look for calculator-like structured content
                        # Calculator apps often have borders or structured displays
                        border_chars = sum(1 for line in lines if any(c in line for c in '+-|='))
                        if border_chars > 3:  # Structured display with borders
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting TUI mode: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up all sessions."""
        for session_id in list(self.sessions.keys()):
            try:
                self.terminate_session(session_id)
            except Exception as e:
                logger.error(f"Error cleaning up session {session_id}: {e}")
