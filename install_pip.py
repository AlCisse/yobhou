#!/usr/bin/env python3
import urllib.request
import subprocess
import sys
import os

# Create .local directory if needed
os.makedirs('/home/node/.local/bin', exist_ok=True)

# Download pip installer
print("Downloading get-pip.py...")
urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "/tmp/get-pip.py")

# Install pip with --break-system-packages
print("Installing pip with --break-system-packages...")
subprocess.check_call([
    sys.executable, "/tmp/get-pip.py",
    "--user",
    "--no-warn-script-location",
    "--break-system-packages"
])

# Add to PATH and verify
print("Checking pip installation...")
subprocess.check_call(['/home/node/.local/bin/pip', '--version'])
print("Pip installed successfully!")
