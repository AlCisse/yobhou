#!/usr/bin/env python3
import subprocess
import os

os.chdir('/home/node/.openclaw/workspace/yobhou/backend')
print("Creating virtual environment...")
subprocess.check_call(['python3', '-m', 'venv', '.venv'])

print("Installing dependencies from requirements.txt...")
subprocess.check_call(['.venv/bin/pip', 'install', '-r', 'requirements.txt'])

print("Running tests...")
subprocess.check_call(['.venv/bin/pytest', '--tb=short'])
