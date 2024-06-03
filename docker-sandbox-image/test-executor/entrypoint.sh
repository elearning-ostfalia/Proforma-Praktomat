#!/bin/bash

echo "Docker entrypoint"

# ls -al 

# ls -al ./..

# ls -al /solution

echo "Copy solution into sandbox"

cp -r /solution/* /sandbox
cp -r /task/* /task

# ls -al 

python3 run_suite.py

ls -al /__result__