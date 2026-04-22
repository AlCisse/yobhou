#!/bin/bash
# Setup virtual environment and run tests
cd /home/node/.openclaw/workspace/yobhou/backend

# Remove existing venv if present
rm -rf .venv

# Create virtual environment manually
mkdir -p .venv/lib/python3.11/site-packages
mkdir -p .venv/bin
mkdir -p .venv/include

# Copy python executable symlink
ln -sf /usr/bin/python3 .venv/bin/python
ln -sf /usr/bin/python3 .venv/bin/python3

# Create pyvenv.cfg
cat > .venv/pyvenv.cfg << 'EOF'
home = /usr/bin
include-system-site-packages = false
version = 3.11.2
EOF

# Install pip to venv using direct pip from ~/.local
export PATH="/home/node/.local/bin:$PATH"
.venv/bin/python -m pip install --upgrade pip 2>/dev/null || .venv/bin/python /tmp/get-pip.py --break-system-packages

# Install dependencies (without PyMuPDF which requires build from source)
.venv/bin/pip install --no-cache-dir -r requirements.txt

# Run tests
.venv/bin/pytest --tb=short -v
