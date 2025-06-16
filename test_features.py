#!/usr/bin/env python3
"""
Test script for terminal-mcp-server features.
This script demonstrates and tests the key features of the terminal-mcp-server.
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Optional

import requests


class TerminalMCPTester:
    """Class for testing Terminal MCP Server features."""

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
    
    def test_simple_command(self):
        """Test running a simple command."""
        self._print_separator("Testing Simple Command")
        
        print("Running 'ls -la' command...")
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": "ls -la", "timeout": 5}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        print(f"Session ID: {session_id}")
        print(f"Output:\n{response['output']}")
        print(f"Exit code: {response['exit_code']}")
        print(f"Running: {response['running']}")
        
        # Wait a bit to ensure the command completes
        time.sleep(1)
        
        # Get the final state
        response = requests.get(f"{self.base_url}/sessions/{session_id}").json()
        print(f"\nFinal state:")
        print(f"Output:\n{response['output']}")
        print(f"Exit code: {response['exit_code']}")
        print(f"Running: {response['running']}")
        
        return session_id
    
    def test_interactive_command(self):
        """Test running an interactive command."""
        self._print_separator("Testing Interactive Command")
        
        print("Running 'python -c \"name = input('Enter your name: '); print(f\\'Hello, {name}!\\')\"' command...")
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": "python -c \"name = input('Enter your name: '); print(f'Hello, {name}!')\"", "timeout": 10}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Send input
        print("\nSending input 'Terminal MCP Tester'...")
        response = requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": "Terminal MCP Tester"}
        ).json()
        
        print(f"Output after input:\n{response['output']}")
        print(f"Exit code: {response['exit_code']}")
        print(f"Running: {response['running']}")
        
        return session_id
    
    def test_long_running_command(self):
        """Test running a long-running command."""
        self._print_separator("Testing Long-Running Command")
        
        print("Running 'sleep 5 && echo Done' command...")
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": "sleep 5 && echo Done", "timeout": 10}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        print(f"Running: {response['running']}")
        
        # Check status after 2 seconds
        print("\nChecking status after 2 seconds...")
        time.sleep(2)
        response = requests.get(f"{self.base_url}/sessions/{session_id}").json()
        print(f"Output:\n{response['output']}")
        print(f"Running: {response['running']}")
        
        # Check status after completion
        print("\nChecking status after completion (waiting 4 more seconds)...")
        time.sleep(4)
        response = requests.get(f"{self.base_url}/sessions/{session_id}").json()
        print(f"Final output:\n{response['output']}")
        print(f"Exit code: {response['exit_code']}")
        print(f"Running: {response['running']}")
        
        return session_id
    
    def test_vim_editor(self):
        """Test using the vim editor."""
        self._print_separator("Testing Vim Editor")
        
        temp_file = "/tmp/vim_test.txt"
        print(f"Starting vim to edit {temp_file}...")
        
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": f"vim {temp_file}", "timeout": 30}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        print(f"Session ID: {session_id}")
        print(f"Initial output:\n{response['output']}")
        
        # Enter insert mode
        print("\nEntering insert mode...")
        response = requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": "i"}
        ).json()
        
        # Type some text
        print("Typing text...")
        text = "This is a test file created by the Terminal MCP Tester.\nIt demonstrates how to interact with vim through the Terminal MCP Server."
        response = requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": text}
        ).json()
        
        # Exit insert mode
        print("\nExiting insert mode...")
        response = requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": "\x1b"}  # Escape key
        ).json()
        
        # Save and quit
        print("Saving and quitting...")
        response = requests.post(
            f"{self.base_url}/send_input",
            json={"session_id": session_id, "input": ":wq\r"}
        ).json()
        
        # Wait for vim to exit
        time.sleep(2)
        
        # Check if vim has exited
        response = requests.get(f"{self.base_url}/sessions/{session_id}").json()
        print(f"\nFinal state:")
        print(f"Output:\n{response['output']}")
        print(f"Exit code: {response['exit_code']}")
        print(f"Running: {response['running']}")
        
        if not response["running"]:
            print(f"File {temp_file} has been created and saved.")
            
            # Verify the file contents
            print("\nVerifying file contents...")
            cat_response = requests.post(
                f"{self.base_url}/run",
                json={"command": f"cat {temp_file}", "timeout": 5}
            ).json()
            
            print(f"File contents:\n{cat_response['output']}")
        
        return session_id
    
    def test_session_management(self):
        """Test session management features."""
        self._print_separator("Testing Session Management")
        
        # List all sessions
        print("Listing all active sessions...")
        response = requests.get(f"{self.base_url}/sessions").json()
        print(f"Active sessions: {response}")
        
        # Create a new session
        print("\nCreating a new session...")
        response = requests.post(
            f"{self.base_url}/run",
            json={"command": "echo 'Session management test' && sleep 10", "timeout": 15}
        ).json()
        
        session_id = response["session_id"]
        self.session_ids.append(session_id)
        
        print(f"Session ID: {session_id}")
        print(f"Output:\n{response['output']}")
        
        # List sessions again
        print("\nListing sessions again...")
        response = requests.get(f"{self.base_url}/sessions").json()
        print(f"Active sessions: {response}")
        
        # Terminate the session
        print(f"\nTerminating session {session_id}...")
        response = requests.delete(f"{self.base_url}/sessions/{session_id}").json()
        print(f"Response: {response}")
        
        # List sessions after termination
        print("\nListing sessions after termination...")
        response = requests.get(f"{self.base_url}/sessions").json()
        print(f"Active sessions: {response}")
        
        return session_id
    
    def test_error_handling(self):
        """Test error handling."""
        self._print_separator("Testing Error Handling")
        
        # Test invalid session ID
        print("Testing invalid session ID...")
        try:
            response = requests.get(f"{self.base_url}/sessions/invalid-session-id")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test invalid command
        print("\nTesting invalid command...")
        try:
            response = requests.post(
                f"{self.base_url}/run",
                json={"command": "nonexistentcommand", "timeout": 5}
            )
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
    
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
            self.test_simple_command()
            self.test_interactive_command()
            self.test_long_running_command()
            self.test_vim_editor()
            self.test_session_management()
            self.test_error_handling()
        finally:
            self.cleanup()


def main():
    """Run the tests."""
    parser = argparse.ArgumentParser(description="Terminal MCP Server Feature Tester")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--test", type=str, choices=["all", "simple", "interactive", "long", "vim", "session", "error"],
        default="all", help="Test to run"
    )
    
    args = parser.parse_args()
    
    tester = TerminalMCPTester(args.url)
    
    try:
        if args.test == "all":
            tester.run_all_tests()
        elif args.test == "simple":
            tester.test_simple_command()
        elif args.test == "interactive":
            tester.test_interactive_command()
        elif args.test == "long":
            tester.test_long_running_command()
        elif args.test == "vim":
            tester.test_vim_editor()
        elif args.test == "session":
            tester.test_session_management()
        elif args.test == "error":
            tester.test_error_handling()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
