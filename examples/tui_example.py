#!/usr/bin/env python3
"""Example of using the Terminal MCP Server with TUI applications."""

import argparse
import json
import sys
import time
from typing import Dict, Optional

import requests


class TerminalMCPClient:
    """Client for the Terminal MCP Server."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            base_url: The base URL of the Terminal MCP Server
        """
        self.base_url = base_url
    
    def run_command(
        self, 
        command: str, 
        timeout: int = 30, 
        session_id: Optional[str] = None,
        use_terminal_emulator: bool = True,
        terminal_emulator: Optional[str] = None
    ) -> Dict:
        """Run a command in a terminal.
        
        Args:
            command: The command to run
            timeout: Timeout in seconds
            session_id: Optional session ID
            use_terminal_emulator: Whether to use a terminal emulator
            terminal_emulator: Terminal emulator to use
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/run"
        payload = {
            "command": command, 
            "timeout": timeout,
            "use_terminal_emulator": use_terminal_emulator
        }
        
        if session_id:
            payload["session_id"] = session_id
        
        if terminal_emulator:
            payload["terminal_emulator"] = terminal_emulator
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def send_input(self, session_id: str, input_text: str) -> Dict:
        """Send input to a terminal session.
        
        Args:
            session_id: The session ID
            input_text: The input to send
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/send_input"
        payload = {"session_id": session_id, "input": input_text}
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str, raw_output: bool = None) -> Dict:
        """Get the current state of a terminal session.
        
        Args:
            session_id: The session ID
            raw_output: Whether to return raw output with ANSI escape sequences
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/sessions/{session_id}"
        params = {}
        
        if raw_output is not None:
            params["raw_output"] = str(raw_output).lower()
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def terminate_session(self, session_id: str) -> Dict:
        """Terminate a terminal session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/sessions/{session_id}"
        
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()
    
    def list_sessions(self) -> Dict:
        """List all active terminal sessions.
        
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/sessions"
        
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def run_htop_example(client: TerminalMCPClient):
    """Run the htop example."""
    print("=== Running htop example ===")
    
    # Start htop in a terminal emulator
    print("Starting htop...")
    response = client.run_command(
        "htop", 
        timeout=60, 
        use_terminal_emulator=True
    )
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print("htop should now be running in a separate terminal window")
    
    # Wait for user to interact with htop
    input("Press Enter after you've interacted with htop...")
    
    # Terminate the session
    print("Terminating htop session...")
    client.terminate_session(session_id)
    print("Session terminated")


def run_vim_example(client: TerminalMCPClient):
    """Run the vim example."""
    print("=== Running vim example ===")
    
    # Create a temporary file to edit
    temp_file = "/tmp/vim_example.txt"
    
    # Start vim in a terminal emulator
    print(f"Starting vim to edit {temp_file}...")
    response = client.run_command(
        f"vim {temp_file}", 
        timeout=60, 
        use_terminal_emulator=True
    )
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print("vim should now be running in a separate terminal window")
    
    # Wait for user to interact with vim
    input("Press Enter after you've edited and saved the file with vim...")
    
    # Terminate the session
    print("Terminating vim session...")
    client.terminate_session(session_id)
    print("Session terminated")
    
    # Check if the file was created
    print(f"Checking if {temp_file} was created...")
    try:
        with open(temp_file, "r") as f:
            content = f.read()
        print(f"File content:\n{content}")
    except FileNotFoundError:
        print(f"File {temp_file} was not created")


def run_nano_example(client: TerminalMCPClient):
    """Run the nano example."""
    print("=== Running nano example ===")
    
    # Create a temporary file to edit
    temp_file = "/tmp/nano_example.txt"
    
    # Start nano in a terminal emulator
    print(f"Starting nano to edit {temp_file}...")
    response = client.run_command(
        f"nano {temp_file}", 
        timeout=60, 
        use_terminal_emulator=True
    )
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print("nano should now be running in a separate terminal window")
    
    # Wait for user to interact with nano
    input("Press Enter after you've edited and saved the file with nano...")
    
    # Terminate the session
    print("Terminating nano session...")
    client.terminate_session(session_id)
    print("Session terminated")
    
    # Check if the file was created
    print(f"Checking if {temp_file} was created...")
    try:
        with open(temp_file, "r") as f:
            content = f.read()
        print(f"File content:\n{content}")
    except FileNotFoundError:
        print(f"File {temp_file} was not created")


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Terminal MCP TUI Example")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--app", type=str, default="all", choices=["all", "htop", "vim", "nano"],
        help="TUI application to test"
    )
    parser.add_argument(
        "--emulator", type=str, default=None, 
        choices=["xterm", "gnome-terminal", "konsole", "tmux"],
        help="Terminal emulator to use"
    )
    
    args = parser.parse_args()
    
    client = TerminalMCPClient(args.url)
    
    if args.app == "all" or args.app == "htop":
        run_htop_example(client)
    
    if args.app == "all" or args.app == "vim":
        run_vim_example(client)
    
    if args.app == "all" or args.app == "nano":
        run_nano_example(client)


if __name__ == "__main__":
    main()
