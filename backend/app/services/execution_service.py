"""
DEPRECATED: Code Execution Service (Legacy)

This file is deprecated. Use DockerSandboxExecutor instead.

The system now uses Docker-based sandbox execution via sandbox_executor.py
"""

from __future__ import annotations


class CodeExecutionService:
    """DEPRECATED - Use DockerSandboxExecutor from sandbox_executor.py"""
    
    def __init__(self):
        raise RuntimeError(
            "CodeExecutionService is deprecated. Use DockerSandboxExecutor from sandbox_executor.py"
        )
