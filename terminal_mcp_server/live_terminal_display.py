"""
Live terminal display window for real-time session viewing.
"""

import tkinter as tk
from tkinter import font, scrolledtext
import threading
import time
import logging
from typing import Optional, Dict, Any, Tuple
from .ansi_to_text_2d import convert_ansi_to_text_2d
from .terminal_screen_emulator import TerminalScreenEmulator

logger = logging.getLogger(__name__)


class LiveTerminalWindow:
    """A live-updating terminal display window."""
    
    def __init__(self, session_id: str, terminal_manager, title: str = "Live Terminal", 
                 update_interval: float = 0.2, width: int = 100, height: int = 40):
        """Initialize the live terminal window.
        
        Args:
            session_id: The terminal session ID to display
            terminal_manager: Reference to the terminal manager
            title: Window title
            update_interval: Update interval in seconds (default: 0.2 = 200ms)
            width: Terminal width in characters
            height: Terminal height in characters
        """
        self.session_id = session_id
        self.terminal_manager = terminal_manager
        self.title = title
        self.update_interval = update_interval
        self.width = width
        self.height = height
        
        self.root = None
        self.text_widget = None
        self.is_running = False
        self.update_thread = None
        self.terminal_emulator = None  # Will be initialized when text_widget is created
        
    def start(self) -> Dict[str, Any]:
        """Start the live terminal display window.
        
        Returns:
            Dict with status information
        """
        try:
            # Create the window in a separate thread to avoid blocking
            self.window_thread = threading.Thread(target=self._create_window, daemon=True)
            self.window_thread.start()
            
            # Give the window a moment to initialize
            time.sleep(0.1)
            
            return {
                "status": "started",
                "session_id": self.session_id,
                "title": self.title,
                "update_interval": self.update_interval,
                "dimensions": f"{self.width}x{self.height}"
            }
            
        except Exception as e:
            logger.error(f"Failed to start live terminal display: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _create_window(self):
        """Create and run the tkinter window."""
        try:
            self.root = tk.Tk()
            self.root.title(f"{self.title} - Session: {self.session_id}")
            
            # Get actual terminal dimensions
            actual_width, actual_height = self._get_terminal_dimensions()
            
            # Calculate window size based on actual terminal dimensions
            # Approximate character size: 8x16 pixels per character
            window_width = max(800, actual_width * 8 + 50)  # Add padding
            window_height = max(600, actual_height * 16 + 50)  # Add padding
            
            self.root.geometry(f"{window_width}x{window_height}")
            
            # Configure the window
            self.root.configure(bg='black')
            
            # Create a monospace font
            terminal_font = font.Font(family="Courier New", size=10)
            
            # Create the text widget with terminal styling using actual dimensions
            self.text_widget = tk.Text(
                self.root,
                font=terminal_font,
                bg='black',
                fg='white',
                insertbackground='white',
                selectbackground='gray',
                wrap=tk.NONE,
                state=tk.DISABLED,
                width=actual_width,
                height=actual_height
            )
            
            # Add scrollbars
            v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.text_widget.yview)
            h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text_widget.xview)
            self.text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Initialize terminal screen emulator
            self.terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
            
            # Pack the widgets
            self.text_widget.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            # Configure grid weights
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)
            
            # Start the update thread
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Start the tkinter main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error creating terminal window: {e}")
            self.is_running = False
    
    def _update_loop(self):
        """Continuously update the terminal display."""
        while self.is_running:
            try:
                if self.root and self.text_widget:
                    # Get the current session output
                    session_data = self.terminal_manager.get_session_output(
                        self.session_id, 
                        raw_output=True
                    )
                    
                    if session_data and 'output' in session_data:
                        # Check if this is a TUI session for better handling
                        is_tui = self._is_tui_session()
                        
                        # Always use raw output, but the color display will handle cleaning
                        terminal_content = session_data['output']
                        
                        # Debug output
                        if hasattr(self, '_last_tui_state'):
                            if self._last_tui_state != is_tui:
                                print(f"[DEBUG] TUI state changed: {self._last_tui_state} -> {is_tui}")
                        self._last_tui_state = is_tui
                        
                        # Update the display on the main thread with colors
                        self.root.after(0, self._update_display_with_colors, terminal_content, is_tui)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(self.update_interval)
    
    def _get_terminal_dimensions(self) -> Tuple[int, int]:
        """Get the actual dimensions of the terminal session.
        
        Returns:
            Tuple of (width, height) from the actual terminal session
        """
        try:
            if self.session_id in self.terminal_manager.sessions:
                session = self.terminal_manager.sessions[self.session_id]
                
                if hasattr(session, 'dimensions'):
                    # dimensions is (rows, cols) but we need (cols, rows) for width, height
                    rows, cols = session.dimensions
                    return cols, rows
                elif hasattr(session, 'screen_buffer') and hasattr(session.screen_buffer, 'cols') and hasattr(session.screen_buffer, 'rows'):
                    # Get from screen buffer if available
                    return session.screen_buffer.cols, session.screen_buffer.rows
            
            # Fallback to the original dimensions passed to the display
            logger.warning(f"Could not get terminal dimensions for session {self.session_id}, using fallback")
            return self.width, self.height
            
        except Exception as e:
            logger.error(f"Error getting terminal dimensions: {e}")
            return self.width, self.height
    
    def _is_tui_session(self) -> bool:
        """Check if the current session is running a TUI application.
        
        Returns:
            True if TUI app is detected, False otherwise
        """
        try:
            if self.session_id in self.terminal_manager.sessions:
                session = self.terminal_manager.sessions[self.session_id]
                return self.terminal_manager._is_tui_active(session)
            return False
        except Exception as e:
            logger.error(f"Error checking TUI status: {e}")
            return False
    
    def _update_display_with_colors(self, content: str, is_tui: bool = False):
        """Update the text widget with new content using proper terminal emulation.
        
        Args:
            content: The terminal content to display with ANSI sequences
            is_tui: Whether this is a TUI application
        """
        try:
            if not self.text_widget:
                print("[DEBUG] No text widget available for update")
                return
                
            # For TUI applications, we need to maintain state across updates
            # For shell sessions, we can create fresh emulator each time
            if is_tui:
                # Maintain terminal emulator state for TUI apps
                if not self.terminal_emulator:
                    try:
                        actual_width, actual_height = self._get_terminal_dimensions()
                        self.terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
                        print(f"[DEBUG] TUI terminal emulator initialized: {actual_width}x{actual_height}")
                    except Exception as init_error:
                        print(f"[DEBUG] Failed to initialize terminal emulator: {init_error}")
                        self._update_display(content)
                        return
                
                # For TUI, we need to be more careful about processing content
                # Only process new content since last update
                if not hasattr(self, '_last_content_length'):
                    self._last_content_length = 0
                
                if len(content) > self._last_content_length:
                    new_content = content[self._last_content_length:]
                    self.terminal_emulator.process_content(new_content)
                    self._last_content_length = len(content)
                elif len(content) < self._last_content_length:
                    # Content was reset (session restarted), start fresh
                    actual_width, actual_height = self._get_terminal_dimensions()
                    self.terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
                    self.terminal_emulator.process_content(content)
                    self._last_content_length = len(content)
                    print("[DEBUG] TUI session reset, fresh emulator created")
            else:
                # For shell sessions, create fresh emulator each time
                # This prevents alternative screen buffer confusion
                try:
                    actual_width, actual_height = self._get_terminal_dimensions()
                    self.terminal_emulator = TerminalScreenEmulator(actual_width, actual_height)
                    self.terminal_emulator.process_content(content)
                    print(f"[DEBUG] Shell session - fresh emulator: {actual_width}x{actual_height}")
                except Exception as init_error:
                    print(f"[DEBUG] Failed to initialize terminal emulator: {init_error}")
                    self._update_display(content)
                    return
            
            print(f"[DEBUG] Processing content. TUI: {is_tui}, Length: {len(content)}")
            
            # Render to the text widget
            self.terminal_emulator.render_to_tkinter(self.text_widget)
            
            print("[DEBUG] Terminal emulation completed successfully")
                
        except Exception as e:
            print(f"[DEBUG] Error in terminal emulation: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            # Fallback to plain text display
            print("[DEBUG] Falling back to plain text display")
            self._update_display(content)
    
    def _update_display(self, content: str):
        """Update the text widget with new content.
        
        Args:
            content: The terminal content to display
        """
        try:
            if self.text_widget:
                # Enable editing temporarily
                self.text_widget.configure(state=tk.NORMAL)
                
                # Clear and update content
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, content)
                
                # Auto-scroll to bottom
                self.text_widget.see(tk.END)
                
                # Disable editing again
                self.text_widget.configure(state=tk.DISABLED)
                
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def _on_close(self):
        """Handle window close event."""
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def stop(self):
        """Stop the live terminal display."""
        self.is_running = False
        if self.root:
            self.root.after(0, self.root.destroy)


class LiveTerminalManager:
    """Manager for live terminal display windows."""
    
    def __init__(self):
        self.active_displays: Dict[str, LiveTerminalWindow] = {}
    
    def show_session_live(self, session_id: str, terminal_manager, 
                         title: Optional[str] = None, 
                         update_interval: float = 0.2,
                         width: int = 100, 
                         height: int = 40) -> Dict[str, Any]:
        """Show a live terminal display for a session.
        
        Args:
            session_id: The terminal session ID to display
            terminal_manager: Reference to the terminal manager
            title: Window title (optional)
            update_interval: Update interval in seconds (default: 0.2)
            width: Terminal width in characters
            height: Terminal height in characters
            
        Returns:
            Dict with status and display information
        """
        try:
            # Check if session exists
            if not terminal_manager.session_exists(session_id):
                return {
                    "status": "error",
                    "error": f"Session {session_id} not found"
                }
            
            # Generate display ID
            display_id = f"{session_id}_live_{int(time.time())}"
            
            # Set default title
            if not title:
                title = f"Live Terminal - {session_id[:8]}"
            
            # Create and start the live display
            live_display = LiveTerminalWindow(
                session_id=session_id,
                terminal_manager=terminal_manager,
                title=title,
                update_interval=update_interval,
                width=width,
                height=height
            )
            
            result = live_display.start()
            
            if result["status"] == "started":
                self.active_displays[display_id] = live_display
                result["display_id"] = display_id
                result["message"] = f"Live terminal display started for session {session_id}"
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to show live session: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stop_display(self, display_id: str) -> Dict[str, Any]:
        """Stop a live terminal display.
        
        Args:
            display_id: The display ID to stop
            
        Returns:
            Dict with status information
        """
        try:
            if display_id in self.active_displays:
                self.active_displays[display_id].stop()
                del self.active_displays[display_id]
                return {
                    "status": "stopped",
                    "display_id": display_id
                }
            else:
                return {
                    "status": "error",
                    "error": f"Display {display_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to stop display: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_displays(self) -> Dict[str, Any]:
        """List all active live displays.
        
        Returns:
            Dict with list of active displays
        """
        displays = []
        for display_id, display in self.active_displays.items():
            displays.append({
                "display_id": display_id,
                "session_id": display.session_id,
                "title": display.title,
                "update_interval": display.update_interval,
                "is_running": display.is_running
            })
        
        return {
            "status": "success",
            "displays": displays,
            "count": len(displays)
        }
    
    def cleanup(self):
        """Clean up all active displays."""
        for display in self.active_displays.values():
            display.stop()
        self.active_displays.clear()
