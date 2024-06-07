# coding=utf-8

import subprocess
import os
import sys


sandbox_dir = '.'

# os.system("ls -al " + sandbox_dir)
# os.system("cd .. && ls -al")  

exec_command = sys.argv[1:]
if isinstance(exec_command, list):
    cmd = exec_command
    cmd.append('--gtest_output=xml')
else:
    cmd = [exec_command, '--gtest_output=xml']

# print(exec_command)
completed_process = subprocess.run(cmd, cwd=sandbox_dir, stderr=subprocess.STDOUT, universal_newlines=True)

# os.system("ls -al " + sandbox_dir)

exit(completed_process.returncode)



