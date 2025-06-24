"""Terminal emulator manager for running TUI applications."""

import logging
import os
import pty
import select
import shlex
import signal
import socket
import subprocess
import tempfile
import threading
import time
import re
import termios
import fcntl
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class TerminalEmulatorSession:
    """Class representing a terminal emulator session."""

    def __init__(
        self, 
        command: str, 
        timeout: int = 30,
        term_type: str = "xterm-256color",
        dimensions: Tuple[int, int] = (40, 100),  # Changed to 40 rows, 100 columns
        emulator: str = "xterm"
    ):
        """Initialize a terminal emulator session.
        
        Args:
            command: The command to run
            timeout: Timeout in seconds
            term_type: Terminal type to emulate
            dimensions: Terminal dimensions (rows, columns)
            emulator: Terminal emulator to use (xterm, gnome-terminal, etc.)
        """
        self.command = command
        self.timeout = timeout
        self.term_type = term_type
        self.dimensions = dimensions
        self.emulator = emulator
        
        self.process = None
        self.output_buffer = ""
        self.exit_code = None
        self.start_time = time.time()
        
        # Use PTY for reliable terminal interaction
        self.master_fd = None
        self.slave_fd = None
        self.running = True
        
        # Start the process with PTY
        self._start_pty_process()
        
        # Start thread to read output
        self.reader_thread = threading.Thread(target=self._read_pty_output)
        self.reader_thread.daemon = True
        self.reader_thread.start()
        
        # Wait for process to start
        time.sleep(0.5)
    
    def _start_pty_process(self):
        """Start process with PTY for direct terminal interaction."""
        try:
            # Create PTY
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Set terminal size
            import struct
            winsize = struct.pack('HHHH', self.dimensions[0], self.dimensions[1], 0, 0)
            fcntl.ioctl(self.slave_fd, termios.TIOCSWINSZ, winsize)
            
            # Start process
            if self.command.strip() in ['bash', 'sh', 'shell']:
                # Interactive shell
                self.process = subprocess.Popen(
                    ['bash', '-i'],
                    stdin=self.slave_fd,
                    stdout=self.slave_fd,
                    stderr=self.slave_fd,
                    preexec_fn=os.setsid,
                    env=dict(os.environ, TERM=self.term_type, PS1='$ ')
                )
            else:
                # Single command, then shell
                self.process = subprocess.Popen(
                    ['bash', '-c', f'{self.command}; exec bash -i'],
                    stdin=self.slave_fd,
                    stdout=self.slave_fd,
                    stderr=self.slave_fd,
                    preexec_fn=os.setsid,
                    env=dict(os.environ, TERM=self.term_type, PS1='$ ')
                )
            
            # Close slave in parent
            os.close(self.slave_fd)
            
            logger.info(f"Started PTY process for command: {self.command}")
            
        except Exception as e:
            logger.error(f"Failed to start PTY process: {e}")
            if self.master_fd:
                os.close(self.master_fd)
            if self.slave_fd:
                os.close(self.slave_fd)
            raise
    
    def _get_window_id(self):
        """Get the window ID of the terminal emulator."""
        if self.emulator in ["xterm", "gnome-terminal", "konsole"]:
            try:
                # Try multiple times as the window might take time to appear
                for _ in range(5):
                    # Get window ID
                    window_id_cmd = ["xdotool", "search", "--name", f"Terminal MCP: {self.command}"]
                    result = subprocess.run(window_id_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        # Get the first window ID (there might be multiple matches)
                        self.window_id = result.stdout.strip().split()[0]
                        logger.info(f"Found window ID: {self.window_id}")
                        return
                    
                    time.sleep(0.5)
                
                logger.warning("Could not find window ID for terminal emulator")
            except Exception as e:
                logger.error(f"Error getting window ID: {e}")
    
    def _read_pty_output(self):
        """Read output from PTY."""
        try:
            while self.running and self.master_fd is not None:
                try:
                    ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                    if ready:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            text = data.decode('utf-8', errors='replace')
                            self.output_buffer += text
                            # Keep buffer reasonable size
                            if len(self.output_buffer) > 50000:
                                self.output_buffer = self.output_buffer[-40000:]
                except (OSError, ValueError):
                    # PTY closed
                    break
                except Exception as e:
                    logger.error(f"Error reading PTY: {e}")
                    break
        except Exception as e:
            logger.error(f"Error in PTY reader: {e}")
    
    def send_input(self, input_text: str) -> str:
        """Send input to the PTY.
        
        Args:
            input_text: The input to send
            
        Returns:
            The current output
        """
        if not self.is_running():
            raise RuntimeError("Process is not running")
        
        try:
            if self.master_fd is not None:
                os.write(self.master_fd, input_text.encode('utf-8'))
                time.sleep(0.1)  # Small delay for output
            
            return self.output_buffer
        except Exception as e:
            logger.error(f"Error sending input to PTY: {e}")
            return self.output_buffer
    
    def get_output(self, raw: bool = None) -> str:
        """Get the current output from the terminal.
        
        Args:
            raw: Ignored, for compatibility with TerminalSession
        Returns:
            The current output
        """
        return self.output_buffer
    
    def capture_screen(self) -> str:
        """Capture the current screen content of the terminal.
        
        Returns:
            The current screen content as text
        """
        if not self.is_running():
            return "Terminal is not running"
        
        try:
            if self.emulator == "tmux":
                # Use tmux's built-in screen capture
                session_name = f"terminal_mcp_{os.path.basename(self.socket_path)}"
                result = subprocess.run(
                    ["tmux", "capture-pane", "-t", session_name, "-p"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error capturing tmux screen: {result.stderr}"
            
            elif self.emulator in ["xterm", "gnome-terminal", "konsole"]:
                # For X11 terminals, try to capture using alternative methods
                try:
                    # Method 1: Try to use xdotool to get window text (limited support)
                    if not self.window_id:
                        self._get_window_id()
                    
                    if self.window_id:
                        # Try to get window title and basic info
                        result = subprocess.run(
                            ["xdotool", "getwindowname", self.window_id],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        window_info = f"Window: {result.stdout.strip()}" if result.returncode == 0 else "Window info unavailable"
                    else:
                        window_info = "Window ID not found"
                    
                    # Method 2: Use the socket output buffer (limited to what was captured)
                    if self.output_buffer:
                        # Try to extract readable content from output buffer
                        readable_content = self._extract_readable_content(self.output_buffer)
                        return f"{window_info}\n\nCaptured Output:\n{readable_content}\n\n[Note: For full screen capture, consider using tmux emulator]"
                    else:
                        return f"{window_info}\n\nNo output captured yet. Screen capture for GUI terminals is limited.\nFor better screen capture, consider using tmux emulator."
                        
                except Exception as e:
                    return f"Error capturing screen: {str(e)}\n[Note: Screen capture for GUI terminals is limited. Consider using tmux.]"
            
            else:
                return "Screen capture not supported for this terminal emulator"
                
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return f"Error capturing screen: {str(e)}"
    
    def _extract_readable_content(self, raw_output: str) -> str:
        """Extract readable content from raw terminal output."""
        if not raw_output:
            return "No content available"
        
        # Remove common ANSI escape sequences
        # Remove escape sequences for colors, cursor movement, etc.
        clean_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_output)
        clean_text = re.sub(r'\x1b\].*?\x07', '', clean_text)  # Remove title sequences
        clean_text = re.sub(r'\x1b[PX^_].*?\x1b\\', '', clean_text)  # Remove other escape sequences
        clean_text = re.sub(r'\x1b[NO]', '', clean_text)  # Remove single-character escapes
        
        # Remove OSC sequences (terminal-specific escape sequences)
        clean_text = re.sub(r'\]697;[^]*?', '', clean_text)
        clean_text = re.sub(r'\]0;[^]*?', '', clean_text)
        
        # Remove control characters except newlines and tabs
        clean_text = ''.join(char for char in clean_text if char.isprintable() or char in '\n\t')
        
        # Extract shell prompts more intelligently
        lines = clean_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Preserve shell prompts and command output
            if ('$' in line and '@' in line) or line.startswith('$') or line.endswith('$'):
                # This looks like a shell prompt
                cleaned_lines.append(line)
            elif line and not line.startswith('\x1b'):
                # This looks like command output
                cleaned_lines.append(line)
        
        # Join lines and add some context
        result = '\n'.join(cleaned_lines)
        
        # If we have output, try to show the last few lines including any prompts
        if result:
            lines = result.split('\n')
            if len(lines) > 20:  # Show last 20 lines
                result = '\n'.join(lines[-20:])
        
        if len(result) > 2000:  # Limit output length
            result = result[:2000] + "\n... (truncated)"
        
        return result if result.strip() else "Terminal ready (no visible output yet)"
    
    def is_running(self) -> bool:
        """Check if the process is still running.
        
        Returns:
            True if the process is running, False otherwise
        """
        if self.process is None:
            return False
        
        return self.process.poll() is None
    
    def terminate(self) -> None:
        """Terminate the process."""
        self.running = False
        
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(0.5)
                
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
        
        # Close PTY
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except:
                pass
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.master_fd is not None:
                os.close(self.master_fd)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def detect_terminal_emulator() -> str:
    """Detect the available terminal emulator.
    
    Returns:
        The name of the available terminal emulator
    """
    # Check for X display first
    if not os.environ.get("DISPLAY"):
        # No X display, use tmux
        try:
            subprocess.run(["which", "tmux"], check=True, stdout=subprocess.PIPE)
            return "tmux"
        except subprocess.CalledProcessError:
            # Fall back to basic terminal
            logger.warning("No X display and tmux not found, terminal emulation may be limited")
            return "basic"
    
    # Check for various terminal emulators
    emulators = ["xterm", "gnome-terminal", "konsole"]
    for emulator in emulators:
        try:
            subprocess.run(["which", emulator], check=True, stdout=subprocess.PIPE)
            return emulator
        except subprocess.CalledProcessError:
            continue
    
    # If we get here, no supported emulator was found
    logger.warning("No supported terminal emulator found, falling back to tmux")
    try:
        subprocess.run(["which", "tmux"], check=True, stdout=subprocess.PIPE)
        return "tmux"
    except subprocess.CalledProcessError:
        logger.warning("tmux not found, terminal emulation may be limited")
        return "basic"
