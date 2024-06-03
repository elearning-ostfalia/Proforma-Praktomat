#!/bin/bash

echo "Docker entrypoint"

date
# ls -al 

# ls -al ./..

# ls -al /solution

echo "Copy solution into sandbox"

cp -r /solution/* /sandbox

echo "Run tests"

python3 run_suite.py

echo "show result folder"

pwd

ls -al /sandbox/__result__

date