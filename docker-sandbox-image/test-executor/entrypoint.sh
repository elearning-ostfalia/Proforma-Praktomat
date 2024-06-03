#!/bin/bash

echo "Docker entrypoint"

# ls -al 

# ls -al ./..

# ls -al /solution

echo "Copy solution into sandbox"

cp -r /solution/* /sandbox

# ls -al 

python3 run_suite.py

ls -al /result