#!/usr/bin/env python3
"""
Utility script to sanitize terminal output by removing ANSI escape sequences.
"""

import re
import sys
import json
import argparse

# Regular expression to match ANSI escape sequences
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi_escape_sequences(text):
    """Strip ANSI escape sequences from text."""
    return ANSI_ESCAPE_PATTERN.sub('', text)

def extract_readable_content(raw_output):
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
    
    return result if result.strip() else "Terminal ready (no visible output yet)"

def extract_calculator_result(text):
    """Extract calculator result from terminal output."""
    # Look for "Result:" followed by any text
    result_match = re.search(r'Result:\s*\|\s*([^|]+)', text)
    if result_match:
        return result_match.group(1).strip()
    
    # Look for "Input:" followed by the calculation
    input_match = re.search(r'Input:\s*\|\s*([^|]+)', text)
    if input_match:
        input_text = input_match.group(1).strip()
        print(f"Found input: {input_text}")
    
    return "Could not extract result"

def main():
    parser = argparse.ArgumentParser(description='Sanitize terminal output')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='File containing terminal output (default: stdin)')
    parser.add_argument('--mode', choices=['strip', 'extract', 'calculator'], default='strip',
                        help='Mode: strip (remove ANSI sequences), extract (extract readable content), '
                             'calculator (extract calculator result)')
    parser.add_argument('--json', action='store_true', help='Parse input as JSON and extract text field')
    
    args = parser.parse_args()
    
    # Read input
    content = args.file.read()
    
    # Parse JSON if requested
    if args.json:
        try:
            data = json.loads(content)
            if isinstance(data, dict) and 'text' in data:
                content = data['text']
            elif isinstance(data, dict) and 'content' in data and isinstance(data['content'], list):
                for item in data['content']:
                    if isinstance(item, dict) and 'text' in item:
                        content = item['text']
                        break
        except json.JSONDecodeError:
            print("Error: Input is not valid JSON", file=sys.stderr)
            return 1
    
    # Process according to mode
    if args.mode == 'strip':
        result = strip_ansi_escape_sequences(content)
    elif args.mode == 'extract':
        result = extract_readable_content(content)
    elif args.mode == 'calculator':
        result = extract_calculator_result(content)
    
    print(result)
    return 0

if __name__ == '__main__':
    sys.exit(main())
