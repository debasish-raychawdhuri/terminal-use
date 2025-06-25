#!/bin/bash

# Create a temporary file
TMP_FILE="/tmp/vim_test_output.txt"

# Write content to the file using vim
xterm -e "vim -c 'normal iHello how are you' -c 'wq' $TMP_FILE"

# Display the content of the file
echo "Content of $TMP_FILE:"
cat $TMP_FILE
