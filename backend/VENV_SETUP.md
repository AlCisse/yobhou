# Virtual Environment Setup for Yobhou Backend

Created by: node
Date: 2026-04-21

## Context
Environment is externally managed (Debian-based) with Python 3.11.
User "node" does not have sudo/root access.

## Solution: Virtual Environment in Project Directory

The project Dockerfile already handles all dependencies:
- Python 3.11-slim base
- All required packages installed via pip in the image build
- No need for local pip installation

## Verify Docker Build Works

```bash
cd /home/node/.openclaw/workspace/yobhou/backend
docker build -t yobhou-backend:latest .
```

This will use the pre-configured Dockerfile which installs:
- Django 5.0.6
- djangorestframework 3.15.1
- djangorestframework-simplejwt 5.3.1
- PaddleOCR and dependencies
- All security/encryption libraries
- All testing frameworks

## Run Tests via Docker

```bash
docker run --rm yobhou-backend:latest pytest backend/
```

Or for interactive testing:

```bash
docker run -it --rm yobhou-backend:latest bash
# Then run pytest or Django commands
```

## Summary
The Docker build is the canonical way to install and test dependencies.
Local pip installation is blocked by externally-managed-environment.
Docker solves this with a clean, reproducible build context.