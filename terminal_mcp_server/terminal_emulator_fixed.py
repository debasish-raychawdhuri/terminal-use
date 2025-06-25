"""Terminal emulator manager for running TUI applications."""

import logging
import os
import pty
import select
import subprocess
import threading
import time
import re
import termios
import fcntl
from typing import Dict, List, Optional, Tuple, Union

from .screen_buffer import TerminalScreenBuffer

logger = logging.getLogger(__name__)

# Regular expression to match ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi_escape_sequences(text: str) -> str:
    """Strip ANSI escape sequences from text."""
    return ANSI_ESCAPE_PATTERN.sub('', text)


class TerminalEmulatorSession:
    """Class representing a terminal emulator session."""

    def __init__(
        self, 
        command: str, 
        timeout: int = 30,
        term_type: str = "xterm-256color",
        dimensions: Tuple[int, int] = (40, 100),
        emulator: str = "xterm"
    ):
        """Initialize a terminal emulator session."""
        self.command = command
        self.timeout = timeout
        self.term_type = term_type
        self.dimensions = dimensions
        self.emulator = emulator
        
        self.process = None
        self.output_buffer = ""
        self.exit_code = None
        self.start_time = time.time()
        
        # Create a unique identifier for this session
        self.session_id = f"term_session_{int(time.time())}_{os.getpid()}"
        
        # Initialize screen buffer for proper terminal display
        self.screen_buffer = TerminalScreenBuffer(dimensions[0], dimensions[1])
        
        # Use PTY for reliable terminal interaction
        self.master_fd = None
        self.slave_fd = None
        self.running = True
        
        # Start the process with PTY
        self._start_pty_process()
        
        # Start thread to read output
        self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self.reader_thread.start()
        logger.info(f"Started reader thread: {self.reader_thread.is_alive()}")
        
        # Wait for process to start
        time.sleep(1)

    def _start_pty_process(self):
        """Start process with PTY for direct terminal interaction."""
        try:
            # Create PTY
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Set terminal size
            import struct
            winsize = struct.pack('HHHH', self.dimensions[0], self.dimensions[1], 0, 0)
            fcntl.ioctl(self.slave_fd, termios.TIOCSWINSZ, winsize)
            
            # Start process directly in PTY
            self.process = subprocess.Popen(
                ['bash', '-c', self.command],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid,
                env=dict(os.environ, TERM=self.term_type)
            )
            
            # Close slave fd in parent process
            os.close(self.slave_fd)
            self.slave_fd = None
            
            logger.info(f"Started PTY process for command: {self.command}")
            
        except Exception as e:
            logger.error(f"Failed to start PTY process: {e}")
            self._cleanup_resources()
            raise

    def _read_output(self):
        """Read output from the terminal."""
        try:
            self._read_pty_output()
        except Exception as e:
            logger.error(f"Error in output reader: {e}")

    def _read_pty_output(self):
        """Read output from PTY."""
        logger.info("Starting PTY output reader thread")
        try:
            while self.running and self.master_fd is not None:
                try:
                    ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                    if ready:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            text = data.decode('utf-8', errors='replace')
                            
                            # Add to raw output buffer for compatibility
                            self.output_buffer += text
                            if len(self.output_buffer) > 50000:
                                self.output_buffer = self.output_buffer[-40000:]
                            
                            # Process through screen buffer for proper display
                            try:
                                self.screen_buffer.process_data(text)
                                logger.info(f"Processed {len(text)} chars, screen buffer now has {len(self.screen_buffer.get_raw_buffer())} chars")
                            except Exception as e:
                                logger.error(f"Error processing data through screen buffer: {e}")
                            
                except (OSError, ValueError) as e:
                    # PTY closed or error
                    if hasattr(e, 'errno') and e.errno not in [5, 9]:  # 5=EIO, 9=EBADF - expected when PTY closes
                        logger.error(f"Error reading PTY: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error reading PTY: {e}")
                    break
                
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    self.exit_code = self.process.returncode
                    self.running = False
                    break
        except Exception as e:
            logger.error(f"Fatal error in PTY reader: {e}")
        finally:
            logger.info("PTY output reader thread ending")

    def send_input(self, input_text: str) -> str:
        """Send input to the terminal."""
        if not self.is_running():
            raise RuntimeError("Process is not running")
        
        try:
            if self.master_fd is not None:
                # Send input directly to the PTY master
                logger.info(f"Sending input to terminal: {input_text!r}")
                os.write(self.master_fd, input_text.encode('utf-8'))
                
                # Give some time for the command to process the input
                time.sleep(0.2)
            else:
                logger.error("No master fd available for sending input")
            
            return self.output_buffer
            
        except Exception as e:
            logger.error(f"Error sending input: {e}")
            return self.output_buffer

    def get_output(self, raw: bool = None) -> str:
        """Get the current output from the terminal."""
        if raw is True:
            # Return raw terminal data
            return self.output_buffer
        elif raw is False:
            # Return cleaned screen content
            return self.screen_buffer.get_screen_content()
        else:
            # Default: return screen content
            return self.screen_buffer.get_screen_content()
    
    def get_screen_content(self) -> str:
        """Get the current screen content as it would appear to a user."""
        return self.screen_buffer.get_screen_content()
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get the current cursor position."""
        return self.screen_buffer.get_cursor_position()
    
    def get_raw_buffer(self) -> str:
        """Get the raw terminal buffer for debugging."""
        return self.screen_buffer.get_raw_buffer()

    def is_running(self) -> bool:
        """Check if the process is still running."""
        return self.process is not None and self.process.poll() is None and self.running

    def terminate(self) -> None:
        """Terminate the process."""
        self.running = False
        
        # Terminate main process
        if self.process and self.process.poll() is None:
            try:
                # Try graceful termination first
                self.process.terminate()
                time.sleep(0.5)
                
                if self.process.poll() is None:
                    # If still running, force kill
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
        
        # Clean up resources
        self._cleanup_resources()

    def _cleanup_resources(self):
        """Clean up resources."""
        try:
            # Close master fd if open
            if hasattr(self, 'master_fd') and self.master_fd is not None:
                os.close(self.master_fd)
                self.master_fd = None
            
            # Close slave fd if open
            if hasattr(self, 'slave_fd') and self.slave_fd is not None:
                os.close(self.slave_fd)
                self.slave_fd = None
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def detect_terminal_emulator() -> str:
    """Detect the available terminal emulator, prioritizing xterm."""
    # Always try xterm first if X display is available
    if os.environ.get("DISPLAY"):
        try:
            subprocess.run(["which", "xterm"], check=True, stdout=subprocess.PIPE)
            logger.info("Using xterm as terminal emulator")
            return "xterm"
        except subprocess.CalledProcessError:
            logger.warning("xterm not found, trying alternatives")
    else:
        logger.warning("No X display available, cannot use xterm")
    
    # If xterm is not available or no X display, try tmux
    try:
        subprocess.run(["which", "tmux"], check=True, stdout=subprocess.PIPE)
        logger.info("Using tmux as terminal emulator")
        return "tmux"
    except subprocess.CalledProcessError:
        pass
    
    # If still no emulator found, try other X11 terminal emulators
    if os.environ.get("DISPLAY"):
        for emulator in ["gnome-terminal", "konsole"]:
            try:
                subprocess.run(["which", emulator], check=True, stdout=subprocess.PIPE)
                logger.info(f"Using {emulator} as terminal emulator")
                return emulator
            except subprocess.CalledProcessError:
                continue
    
    # If we get here, no supported emulator was found
    logger.warning("No supported terminal emulator found, falling back to basic")
    return "basic"
