#!/usr/bin/env python3
"""
Create virtualenv manually with pip bootstrap.
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import tempfile

def create_venv_with_pip(path):
    """Create a virtual environment and install pip."""
    
    # Clean up existing venv if present
    if os.path.exists(path):
        shutil.rmtree(path)
    
    # Create directory structure
    os.makedirs(path)
    os.makedirs(os.path.join(path, 'lib', 'python' + sys.version[:3], 'site-packages'))
    os.makedirs(os.path.join(path, 'bin'))
    os.makedirs(os.path.join(path, 'include'))
    
    # Copy python executable symlink
    python_path = sys.executable
    os.symlink(python_path, os.path.join(path, 'bin', 'python'))
    os.symlink(python_path, os.path.join(path, 'bin', 'python3'))
    
    # Create pyvenv.cfg
    venv_cfg = f"""home = {os.path.dirname(python_path)}
include-system-site-packages = false
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
"""
    with open(os.path.join(path, 'pyvenv.cfg'), 'w') as f:
        f.write(venv_cfg)
    
    print(f"Virtual environment created at {path}")
    
    # Install pip using get-pip.py in the venv
    print("Installing pip to venv...")
    get_pip_script = os.path.join(path, 'get-pip.py')
    try:
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip_script)
        
        subprocess.check_call([
            os.path.join(path, 'bin', 'python'),
            get_pip_script,
            '--break-system-packages'
        ])
        
        print("Pip installed successfully!")
        
    finally:
        if os.path.exists(get_pip_script):
            os.remove(get_pip_script)

def install_requirements(venv_path, req_file):
    """Install requirements from file."""
    print(f"Installing dependencies from {req_file}...")
    subprocess.check_call([
        os.path.join(venv_path, 'bin', 'pip'),
        'install', '-r', req_file
    ])
    print("Dependencies installed!")

def run_tests(venv_path):
    """Run pytest tests."""
    print("Running tests...")
    result = subprocess.run([
        os.path.join(venv_path, 'bin', 'pytest'),
        '--tb=short', '-v'
    ])
    return result.returncode

if __name__ == '__main__':
    venv_path = '/home/node/.openclaw/workspace/yobhou/backend/.venv'
    req_file = '/home/node/.openclaw/workspace/yobhou/backend/requirements.txt'
    
    create_venv_with_pip(venv_path)
    install_requirements(venv_path, req_file)
    exit_code = run_tests(venv_path)
    
    sys.exit(exit_code)
