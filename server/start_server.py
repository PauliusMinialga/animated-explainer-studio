#!/usr/bin/env python3
"""
Launcher that detaches from the controlling terminal before starting uvicorn.
This prevents SIGTTOU when subprocesses (manim, ffmpeg) probe the terminal.
"""
import os
import sys

# Create a new session — fully detaches from the shell's process group/terminal
os.setsid()

# Replace this process with uvicorn
os.execv(
    sys.argv[1],  # python interpreter path
    [sys.argv[1], "-m", "uvicorn", "main:app",
     "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
)
