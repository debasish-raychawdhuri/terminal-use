#!/usr/bin/env python3
"""
Test script for terminal MCP server with xterm
"""

import os
import subprocess
import time
import sys

def main():
    """Main function to test xterm integration."""
    print("Testing terminal MCP server with xterm...")
    
    # Check if xterm is available
    try:
        subprocess.run(["which", "xterm"], check=True, stdout=subprocess.PIPE)
        print("xterm is available")
    except subprocess.CalledProcessError:
        print("xterm is not available, please install it")
        return 1
    
    # Create a test file
    with open("/tmp/test_vim_content.txt", "w") as f:
        f.write("Hello how are you\n")
    
    # Run vim with the test file
    print("Running vim with test file...")
    try:
        # Use xterm directly to open vim
        process = subprocess.Popen([
            "xterm", 
            "-title", "Test Vim Session", 
            "-e", 
            "vim /tmp/test_vim_content.txt"
        ])
        
        print("Vim is now running in xterm. Please interact with it.")
        print("Press Ctrl+C to terminate the test.")
        
        # Wait for the process to complete or user to interrupt
        while process.poll() is None:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        if process and process.poll() is None:
            process.terminate()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    # Read the content of the file
    try:
        with open("/tmp/test_vim_content.txt", "r") as f:
            content = f.read()
        print(f"Content of the file after editing:\n{content}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
