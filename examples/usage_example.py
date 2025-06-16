#!/usr/bin/env python3
"""Example usage of the Terminal MCP Server client."""

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
        self, command: str, timeout: int = 30, session_id: Optional[str] = None
    ) -> Dict:
        """Run a command in a terminal.
        
        Args:
            command: The command to run
            timeout: Timeout in seconds
            session_id: Optional session ID
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/run"
        payload = {"command": command, "timeout": timeout}
        if session_id:
            payload["session_id"] = session_id
        
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
    
    def get_session(self, session_id: str) -> Dict:
        """Get the current state of a terminal session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Response from the server
        """
        url = f"{self.base_url}/sessions/{session_id}"
        
        response = requests.get(url)
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


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="Terminal MCP Client Example")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--command", type=str, default="top", help="Command to run"
    )
    
    args = parser.parse_args()
    
    client = TerminalMCPClient(args.url)
    
    print(f"Running command: {args.command}")
    response = client.run_command(args.command)
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print(f"Initial output:\n{response['output']}")
    
    # If the command is still running, we can interact with it
    if response["running"]:
        print("\nPress Ctrl+C to exit. Enter commands to send to the terminal:")
        try:
            while True:
                user_input = input("> ")
                if not user_input:
                    # Just get the current state
                    response = client.get_session(session_id)
                else:
                    # Send input
                    response = client.send_input(session_id, user_input)
                
                print(f"Output:\n{response['output']}")
                
                # Check if the command is still running
                if not response["running"]:
                    print(f"Command exited with code: {response['exit_code']}")
                    break
        except KeyboardInterrupt:
            print("\nTerminating session...")
            client.terminate_session(session_id)
    else:
        print(f"Command exited with code: {response['exit_code']}")


if __name__ == "__main__":
    main()
