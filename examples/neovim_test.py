#!/usr/bin/env python3
"""Example of using the Terminal MCP Server with Neovim."""

import argparse
import sys
import time

import requests


def main():
    """Run the neovim example."""
    parser = argparse.ArgumentParser(description="Neovim Example")
    parser.add_argument(
        "--url", type=str, default="http://localhost:8000", help="URL of the Terminal MCP Server"
    )
    parser.add_argument(
        "--file", type=str, default="/tmp/hello_world.py", help="File to edit with neovim"
    )
    parser.add_argument(
        "--emulator", type=str, default="xterm", 
        choices=["xterm", "gnome-terminal", "konsole", "tmux"],
        help="Terminal emulator to use"
    )
    
    args = parser.parse_args()
    
    # Start neovim in a terminal emulator
    print(f"Starting neovim to edit {args.file}...")
    response = requests.post(
        f"{args.url}/run",
        json={
            "command": f"nvim {args.file}", 
            "timeout": 60,
            "use_terminal_emulator": True,
            "terminal_emulator": args.emulator
        }
    ).json()
    
    session_id = response["session_id"]
    print(f"Session ID: {session_id}")
    print("neovim should now be running in a separate terminal window")
    
    # Wait for neovim to initialize
    time.sleep(2)
    
    # Enter insert mode
    print("Entering insert mode (i)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "i"}
    )
    time.sleep(0.5)
    
    # Type the Python hello world program
    print("Typing Python hello world program...")
    python_code = '#!/usr/bin/env python3\n\nprint("Hello, World!")\n'
    
    # Send text in smaller chunks to avoid issues
    for chunk in [python_code[i:i+20] for i in range(0, len(python_code), 20)]:
        requests.post(
            f"{args.url}/send_input",
            json={"session_id": session_id, "input": chunk}
        )
        time.sleep(0.2)
    
    # Exit insert mode
    print("Exiting insert mode (Escape)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "\x1b"}
    )
    time.sleep(0.5)
    
    # Save and quit
    print("Saving and quitting (:wq)...")
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": ":"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "w"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "q"}
    )
    time.sleep(0.2)
    
    requests.post(
        f"{args.url}/send_input",
        json={"session_id": session_id, "input": "\r"}
    )
    
    # Wait for neovim to exit
    time.sleep(2)
    
    # Check if neovim has exited
    response = requests.get(f"{args.url}/sessions/{session_id}").json()
    if not response["running"]:
        print(f"neovim exited with code: {response['exit_code']}")
    else:
        print("neovim is still running, terminating session...")
        requests.delete(f"{args.url}/sessions/{session_id}")
    
    # Check if the file was created
    try:
        with open(args.file, "r") as f:
            content = f.read()
        print(f"\nFile content:\n{content}")
        
        # Make the file executable
        print("Making the file executable...")
        import os
        os.chmod(args.file, 0o755)
        
        # Run the Python script
        print("\nRunning the Python script:")
        import subprocess
        result = subprocess.run([args.file], capture_output=True, text=True)
        print(f"Output: {result.stdout}")
        
    except FileNotFoundError:
        print(f"\nFile {args.file} was not created")


if __name__ == "__main__":
    main()
