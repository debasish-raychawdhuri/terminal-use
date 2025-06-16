#!/usr/bin/env python3
"""
Test script for terminal-mcp-server with various TUI applications.
This script tests the server's ability to handle different terminal-based
user interface applications that would normally cause AI agents to hang.
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Optional

import requests


class TUIApplicationTester:
    """Class for testing Terminal MCP Server with TUI applications."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the tester.
        
        Args:
            base_url: The base URL of the Terminal MCP Server
        """
        self.base_url = base_url
        self.session_ids = []
    
    def _print_separator(self, title: str):
        """Print a separator with a title.
        
        Args:
            title: The title to print
        """
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80 + "\n")
    
    def _run_command(self, command: str, timeout: int = 30) -> Dict:
        """Run a command and return the response.
        
        Args:
            command: The command to run
            timeout: Timeout in seconds
            
        Returns:
            The response from the server
        """
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": command, "timeout": timeout}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        return response
    
    def _send_input(self, session_id: str, input_text: str) -> Dict:
        """Send input to a session and return the response.
        
        Args:
            session_id: The session ID
            input_text: The input to send
            
        Returns:
            The response from the server
        """
        return requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": input_text}
        ).json()
    
    def _get_session(self, session_id: str) -> Dict:
        """Get the current state of a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            The response from the server
        """
        return requests.get(f"{self.base_url}/sessions/{session_id}").json()
    
    def test_htop(self):
        """Test the htop application."""
        self._print_separator("Testing htop")
        
        print("Starting htop...")
        response = self._run_command("htop", timeout=60)
        session_id = response["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Wait for htop to initialize
        time.sleep(2)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"\nUpdated output:\n{response['output']}")
        
        # Send some keystrokes to interact with htop
        print("\nSending 'F2' to open setup...")
        self._send_input(session_id, "\x1bOQ")  # F2 key
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"Setup screen:\n{response['output']}")
        
        # Send Escape to exit setup
        print("\nSending 'Escape' to exit setup...")
        self._send_input(session_id, "\x1b")  # Escape key
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"Back to main screen:\n{response['output']}")
        
        # Send 'q' to quit htop
        print("\nSending 'q' to quit htop...")
        self._send_input(session_id, "q")
        time.sleep(1)
        
        # Check if htop has exited
        response = self._get_session(session_id)
        if not response["running"]:
            print(f"htop exited with code: {response['exit_code']}")
        else:
            print("htop is still running, terminating session...")
            requests.delete(f"{self.base_url}/sessions/{session_id}")
        
        return session_id
    
    def test_nano(self):
        """Test the nano text editor."""
        self._print_separator("Testing nano")
        
        temp_file = "/tmp/nano_test.txt"
        print(f"Starting nano to edit {temp_file}...")
        
        response = self._run_command(f"nano {temp_file}", timeout=60)
        session_id = response["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Wait for nano to initialize
        time.sleep(1)
        
        # Type some text
        print("\nTyping text...")
        text = "This is a test file created with nano through the Terminal MCP Server.\n\nIt demonstrates how AI agents can interact with terminal-based applications."
        self._send_input(session_id, text)
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"After typing:\n{response['output']}")
        
        # Save the file (Ctrl+O)
        print("\nSaving the file (Ctrl+O)...")
        self._send_input(session_id, "\x0f")  # Ctrl+O
        time.sleep(1)
        
        # Press Enter to confirm filename
        print("Confirming filename...")
        self._send_input(session_id, "\r")
        time.sleep(1)
        
        # Exit nano (Ctrl+X)
        print("\nExiting nano (Ctrl+X)...")
        self._send_input(session_id, "\x18")  # Ctrl+X
        time.sleep(1)
        
        # Check if nano has exited
        response = self._get_session(session_id)
        if not response["running"]:
            print(f"nano exited with code: {response['exit_code']}")
            
            # Verify the file contents
            print("\nVerifying file contents...")
            cat_response = self._run_command(f"cat {temp_file}", timeout=5)
            print(f"File contents:\n{cat_response['output']}")
        else:
            print("nano is still running, terminating session...")
            requests.delete(f"{self.base_url}/sessions/{session_id}")
        
        return session_id
    
    def test_less(self):
        """Test the less pager."""
        self._print_separator("Testing less")
        
        # Create a test file with multiple lines
        test_file = "/tmp/less_test.txt"
        print(f"Creating test file {test_file}...")
        
        create_file_cmd = f"echo -e 'Line 1\\nLine 2\\nLine 3\\nLine 4\\nLine 5\\nLine 6\\nLine 7\\nLine 8\\nLine 9\\nLine 10\\nLine 11\\nLine 12\\nLine 13\\nLine 14\\nLine 15\\nLine 16\\nLine 17\\nLine 18\\nLine 19\\nLine 20' > {test_file}"
        self._run_command(create_file_cmd, timeout=5)
        
        # Start less
        print(f"\nStarting less to view {test_file}...")
        response = self._run_command(f"less {test_file}", timeout=30)
        session_id = response["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Wait for less to initialize
        time.sleep(1)
        
        # Press space to go to next page
        print("\nPressing space to go to next page...")
        self._send_input(session_id, " ")
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"After space:\n{response['output']}")
        
        # Press 'g' to go to beginning
        print("\nPressing 'g' to go to beginning...")
        self._send_input(session_id, "g")
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"After 'g':\n{response['output']}")
        
        # Press 'G' to go to end
        print("\nPressing 'G' to go to end...")
        self._send_input(session_id, "G")
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"After 'G':\n{response['output']}")
        
        # Press 'q' to quit
        print("\nPressing 'q' to quit...")
        self._send_input(session_id, "q")
        time.sleep(1)
        
        # Check if less has exited
        response = self._get_session(session_id)
        if not response["running"]:
            print(f"less exited with code: {response['exit_code']}")
        else:
            print("less is still running, terminating session...")
            requests.delete(f"{self.base_url}/sessions/{session_id}")
        
        return session_id
    
    def test_top(self):
        """Test the top command."""
        self._print_separator("Testing top")
        
        print("Starting top...")
        response = self._run_command("top -b -n 1", timeout=30)
        session_id = response["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"Output:\n{response['output']}")
        
        # Wait for top to complete
        time.sleep(2)
        
        # Check if top has exited
        response = self._get_session(session_id)
        if not response["running"]:
            print(f"top exited with code: {response['exit_code']}")
        else:
            print("top is still running, terminating session...")
            requests.delete(f"{self.base_url}/sessions/{session_id}")
        
        # Now run interactive top
        print("\nStarting interactive top...")
        response = self._run_command("top", timeout=30)
        session_id = response["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Wait for top to initialize
        time.sleep(1)
        
        # Press 'h' for help
        print("\nPressing 'h' for help...")
        self._send_input(session_id, "h")
        time.sleep(1)
        
        # Get updated output
        response = self._get_session(session_id)
        print(f"Help screen:\n{response['output']}")
        
        # Press 'q' to exit help
        print("\nPressing 'q' to exit help...")
        self._send_input(session_id, "q")
        time.sleep(1)
        
        # Press 'q' to quit top
        print("\nPressing 'q' to quit top...")
        self._send_input(session_id, "q")
        time.sleep(1)
        
        # Check if top has exited
        response = self._get_session(session_id)
        if not response["running"]:
            print(f"top exited with code: {response['exit_code']}")
        else:
            print("top is still running, terminating session...")
            requests.delete(f"{self.base_url}/sessions/{session_id}")
        
        return session_id
    
    def cleanup(self):
        """Clean up all sessions."""
        self._print_separator("Cleaning Up")
        
        print(f"Cleaning up {len(self.session_ids)} sessions...")
        
        for session_id in self.session_ids:
            try:
                print(f"Terminating session {session_id}...")
                requests.delete(f"{self.base_url}/sessions/{session_id}")
            except Exception as e:
                print(f"Error terminating session {session_id}: {e}")
        
        print("\nFinal session list:")
        response = requests.get(f"{self.base_url}/sessions").json()
        print(f"Active sessions: {response}")
    
    def run_all_tests(self):
        """Run all tests."""
        try:
            self.test_htop()
            self.test_nano()
            self.test_less()
            self.test_top()
        finally:
            self.cleanup()


def main():
    """Run the tests."""
    parser = argparse.ArgumentParser(description="Terminal MCP Server TUI Application Tester")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--test", type=str, choices=["all", "htop", "nano", "less", "top"],
        default="all", help="Test to run"
    )
    
    args = parser.parse_args()
    
    tester = TUIApplicationTester(args.url)
    
    try:
        if args.test == "all":
            tester.run_all_tests()
        elif args.test == "htop":
            tester.test_htop()
        elif args.test == "nano":
            tester.test_nano()
        elif args.test == "less":
            tester.test_less()
        elif args.test == "top":
            tester.test_top()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
