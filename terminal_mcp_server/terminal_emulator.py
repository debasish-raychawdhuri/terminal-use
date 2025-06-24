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
        self.window_id = None
        self.raw_output_buffer = ""  # Store raw terminal output including escape sequences
        
        # Create a socket pair for communication
        self.socket_dir = tempfile.mkdtemp()
        self.socket_path = os.path.join(self.socket_dir, "terminal.sock")
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(1)
        
        # Create a script to run in the terminal
        self.script_path = os.path.join(self.socket_dir, "run_command.sh")
        with open(self.script_path, "w") as f:
            f.write(f"""#!/bin/bash
export TERM={self.term_type}
# Run the command and capture its output
{command} 2>&1 | tee >(nc -U {self.socket_path})
exit_code=${{PIPESTATUS[0]}}
# Send exit code
echo -e "\\n__EXIT_CODE__${{exit_code}}__" | nc -U {self.socket_path}
""")
        os.chmod(self.script_path, 0o755)
        
        # Start the terminal emulator
        self._start_terminal_emulator()
        
        # Start a thread to read from the socket
        self.running = True
        self.reader_thread = threading.Thread(target=self._read_from_socket)
        self.reader_thread.daemon = True
        self.reader_thread.start()
        
        # Wait a moment for the terminal to initialize
        time.sleep(1)
        
        # Get the window ID
        self._get_window_id()
    
    def _start_terminal_emulator(self):
        """Start the terminal emulator."""
        try:
            if self.emulator == "xterm":
                cmd = [
                    "xterm",
                    "-T", f"Terminal MCP: {self.command}",
                    "-geometry", f"{self.dimensions[1]}x{self.dimensions[0]}",
                    "-e", self.script_path
                ]
            elif self.emulator == "gnome-terminal":
                cmd = [
                    "gnome-terminal",
                    "--title", f"Terminal MCP: {self.command}",
                    "--geometry", f"{self.dimensions[1]}x{self.dimensions[0]}",
                    "--", self.script_path
                ]
            elif self.emulator == "konsole":
                cmd = [
                    "konsole",
                    "--title", f"Terminal MCP: {self.command}",
                    "--geometry", f"{self.dimensions[1]}x{self.dimensions[0]}",
                    "-e", self.script_path
                ]
            elif self.emulator == "tmux":
                # Create a new detached tmux session
                session_name = f"terminal_mcp_{os.path.basename(self.socket_path)}"
                cmd = [
                    "tmux", "new-session", 
                    "-d", "-s", session_name,
                    self.script_path
                ]
            else:
                raise ValueError(f"Unsupported terminal emulator: {self.emulator}")
            
            logger.info(f"Starting terminal emulator with command: {' '.join(cmd)}")
            self.process = subprocess.Popen(cmd)
            
        except Exception as e:
            logger.error(f"Failed to start terminal emulator: {e}")
            self.cleanup()
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
    
    def _read_from_socket(self):
        """Read from the socket in a separate thread."""
        try:
            client_socket, _ = self.server_socket.accept()
            client_socket.settimeout(0.5)  # Short timeout for non-blocking reads
            
            buffer = ""
            while self.running:
                try:
                    data = client_socket.recv(4096).decode("utf-8", errors="replace")
                    if not data:
                        # Connection closed
                        break
                    
                    buffer += data
                    
                    # Check for exit code marker
                    if "__EXIT_CODE__" in buffer:
                        parts = buffer.split("__EXIT_CODE__")
                        if len(parts) > 1 and "__" in parts[1]:
                            code_parts = parts[1].split("__")
                            if code_parts[0].isdigit():
                                self.exit_code = int(code_parts[0])
                                buffer = parts[0] + code_parts[1]
                    
                    self.output_buffer = buffer
                    
                except socket.timeout:
                    # This is expected for the non-blocking reads
                    continue
                except Exception as e:
                    logger.error(f"Error reading from socket: {e}")
                    break
            
            client_socket.close()
            
        except Exception as e:
            logger.error(f"Error in socket communication: {e}")
        finally:
            self.server_socket.close()
    
    def send_input(self, input_text: str) -> str:
        """Send input to the terminal.
        
        Args:
            input_text: The input to send
            
        Returns:
            The current output
        """
        if not self.is_running():
            raise RuntimeError("Process is not running")
        
        # For terminal emulators, we need to use tools like xdotool to send keystrokes
        try:
            if self.emulator in ["xterm", "gnome-terminal", "konsole"]:
                if not self.window_id:
                    self._get_window_id()
                
                if not self.window_id:
                    logger.error("Cannot send input: Window ID not found")
                    return self.output_buffer
                
                # Activate window
                subprocess.run(["xdotool", "windowactivate", self.window_id])
                time.sleep(0.2)  # Wait for window to activate
                
                # Handle special keys
                if input_text == "\x1b":  # Escape key
                    subprocess.run(["xdotool", "key", "Escape"])
                elif input_text == "\r":  # Enter key
                    subprocess.run(["xdotool", "key", "Return"])
                elif input_text == "\t":  # Tab key
                    subprocess.run(["xdotool", "key", "Tab"])
                elif input_text == "\x7f" or input_text == "\b":  # Backspace
                    subprocess.run(["xdotool", "key", "BackSpace"])
                elif input_text.startswith("\x1b["):  # Arrow keys and others
                    if input_text == "\x1b[A":  # Up arrow
                        subprocess.run(["xdotool", "key", "Up"])
                    elif input_text == "\x1b[B":  # Down arrow
                        subprocess.run(["xdotool", "key", "Down"])
                    elif input_text == "\x1b[C":  # Right arrow
                        subprocess.run(["xdotool", "key", "Right"])
                    elif input_text == "\x1b[D":  # Left arrow
                        subprocess.run(["xdotool", "key", "Left"])
                else:
                    # For normal text, use type
                    subprocess.run(["xdotool", "type", input_text])
                
            elif self.emulator == "tmux":
                # Send keystrokes to tmux session
                session_name = f"terminal_mcp_{os.path.basename(self.socket_path)}"
                subprocess.run(["tmux", "send-keys", "-t", session_name, input_text])
            
            # Wait a bit for the command to process
            time.sleep(0.2)
            
            return self.output_buffer
        except Exception as e:
            logger.error(f"Error sending input: {e}")
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
        
        # Remove control characters except newlines and tabs
        clean_text = ''.join(char for char in clean_text if char.isprintable() or char in '\n\t')
        
        # Clean up excessive whitespace but preserve structure
        lines = clean_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove trailing whitespace but keep leading whitespace for indentation
            cleaned_line = line.rstrip()
            if cleaned_line or (cleaned_lines and cleaned_lines[-1]):  # Keep empty lines between content
                cleaned_lines.append(cleaned_line)
        
        # Join lines and limit length
        result = '\n'.join(cleaned_lines)
        if len(result) > 2000:  # Limit output length
            result = result[:2000] + "\n... (truncated)"
        
        return result if result.strip() else "No readable content found"
    
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
        
        # Clean up tmux session if used
        if self.emulator == "tmux":
            try:
                session_name = f"terminal_mcp_{os.path.basename(self.socket_path)}"
                subprocess.run(["tmux", "kill-session", "-t", session_name], 
                               stderr=subprocess.DEVNULL)
            except Exception as e:
                logger.error(f"Error cleaning up tmux session: {e}")
        
        self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Close socket
            if hasattr(self, 'server_socket'):
                self.server_socket.close()
            
            # Remove socket file and directory
            if hasattr(self, 'socket_path') and os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
            
            if hasattr(self, 'script_path') and os.path.exists(self.script_path):
                os.unlink(self.script_path)
            
            if hasattr(self, 'socket_dir') and os.path.exists(self.socket_dir):
                os.rmdir(self.socket_dir)
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
