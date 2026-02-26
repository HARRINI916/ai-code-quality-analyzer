"""
Secure Sandbox Code Executor using Docker Containers

This module provides secure, isolated code execution using Docker containers
with strict resource limits, network isolation, and execution timeouts.

Security Features:
- No exec() or eval() operations
- Docker container isolation
- Read-only filesystem
- CPU and memory limits
- Network access disabled
- Execution timeout (2-5 seconds)
"""

from __future__ import annotations

import os
import shlex
import tempfile
import time
from dataclasses import dataclass
from typing import Any
from typing import Optional

from .io_compat import inject_python_execution_print_fallback
from .output_comparator import compare_outputs

try:
    import docker
except Exception:  # pragma: no cover - optional dependency at runtime
    docker = None


@dataclass
class ExecutionResult:
    """Result of a code execution"""
    status: str  # "success" or "error"
    stdout: str
    stderr: str
    execution_time_ms: float
    exit_code: int


@dataclass
class TestCaseResult:
    """Result of a single test case"""
    input_data: str
    expected_output: str
    actual_output: str
    passed: bool
    error: Optional[str] = None


class DockerSandboxExecutor:
    """
    Executes code safely in isolated Docker containers.
    
    Supported languages: python, c, cpp, java
    """
    
    # Docker image mappings for each language
    LANGUAGE_IMAGES = {
        "python": "python:3.11-slim",
        "c": "gcc:latest",
        "cpp": "gcc:latest",
        "java": "openjdk:17-slim",
    }
    
    # Command templates for running code
    LANGUAGE_COMMANDS = {
        "python": "python /code/script.py",
        "c": "cd /code && gcc -o program program.c && ./program",
        "cpp": "cd /code && g++ -o program program.cpp && ./program",
        "java": "cd /code && javac Main.java && java Main",
    }
    
    # File extensions
    LANGUAGE_EXTENSIONS = {
        "python": "py",
        "c": "c",
        "cpp": "cpp",
        "java": "java",
    }
    
    # Execution timeouts (seconds)
    EXEC_TIMEOUT_SECONDS = 5
    
    # Resource limits
    MEMORY_LIMIT = "128m"
    CPU_LIMIT = 0.5
    
    def __init__(self):
        """Initialize Docker executor (lazy connection)"""
        self.client = None
    
    def _ensure_connected(self):
        """Ensure Docker client is connected"""
        if docker is None:
            raise RuntimeError(
                "Docker SDK is not installed. Install backend dependencies (including 'docker') to enable sandbox execution."
            )

        if self.client is None:
            try:
                self.client = docker.from_env()
                self.client.ping()
            except Exception as e:
                raise RuntimeError(
                    f"Docker connection failed: {str(e)}. "
                    f"Ensure Docker is installed and running."
                )
    
    def execute_with_test_cases(
        self,
        code: str,
        language: str,
        test_cases: list[dict]
    ) -> dict:
        """
        Execute code with test cases in a sandbox.
        
        Args:
            code: Source code to execute
            language: Programming language (python, c, cpp, java)
            test_cases: List of {"input": "...", "expected_output": "..."} dicts
            
        Returns:
            {
                "status": "success" or "error",
                "execution_time_ms": float,
                "results": [TestCaseResult...],
                "stdout": "",
                "stderr": ""
            }
        """
        
        # Ensure Docker connection
        self._ensure_connected()
        
        if language not in self.LANGUAGE_IMAGES:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}",
                "execution_time_ms": 0,
                "results": [],
                "stdout": "",
                "stderr": ""
            }
        
        results = []
        total_stdout = ""
        total_stderr = ""
        start_time = time.time()

        try:
            if not test_cases:
                simple_result = self.execute_simple(code, language)
                if simple_result.status == "error":
                    return {
                        "status": "error",
                        "error": simple_result.stderr or "Execution failed",
                        "execution_time_ms": simple_result.execution_time_ms,
                        "results": [],
                        "stdout": simple_result.stdout,
                        "stderr": simple_result.stderr,
                    }
                return {
                    "status": "success",
                    "execution_time_ms": simple_result.execution_time_ms,
                    "results": [],
                    "stdout": simple_result.stdout,
                    "stderr": simple_result.stderr,
                }

            for test_case in test_cases:
                result = self._run_test_case(
                    code,
                    language,
                    test_case.get("input", ""),
                    test_case.get("expected_output", "")
                )
                
                results.append(result)
                total_stdout += result["actual_output"]
                if result.get("error"):
                    total_stderr += result["error"] + "\n"
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "success",
                "execution_time_ms": execution_time_ms,
                "results": results,
                "stdout": total_stdout,
                "stderr": total_stderr
            }
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "error": str(e),
                "execution_time_ms": execution_time_ms,
                "results": results,
                "stdout": total_stdout,
                "stderr": total_stderr
            }
    
    def _run_test_case(
        self,
        code: str,
        language: str,
        input_data: str,
        expected_output: str
    ) -> dict:
        """Run a single test case"""
        
        container = None
        try:
            # Create temporary directory and file
            with tempfile.TemporaryDirectory() as tmp_dir:
                self._write_code_file(code, language, tmp_dir)
                
                # Create and run container
                container = self._create_container(language, tmp_dir)
                
                # Execute code with input
                actual_output = self._execute_in_container(
                    container,
                    language,
                    input_data
                )

                # Fallback: if Python code produced no stdout, retry with a safe print-wrapper.
                if language == "python" and not actual_output.strip() and expected_output.strip():
                    fallback_code = inject_python_execution_print_fallback(code, original_code=code)
                    if fallback_code != code:
                        self._write_code_file(fallback_code, language, tmp_dir)
                        actual_output = self._execute_in_container(
                            container,
                            language,
                            input_data
                        )
                
                passed, normalized_expected, normalized_actual = compare_outputs(expected_output, actual_output)
                
                return {
                    "input": input_data,
                    "expected_output": normalized_expected,
                    "actual_output": normalized_actual,
                    "passed": passed,
                    "error": None
                }
                
        except Exception as e:
            return {
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": "",
                "passed": False,
                "error": str(e)
            }
        finally:
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove()
                except Exception:
                    pass
    
    def _write_code_file(self, code: str, language: str, tmp_dir: str) -> str:
        """Write code to temporary file"""
        
        if language == "python":
            filename = "script.py"
        elif language == "c":
            filename = "program.c"
        elif language == "cpp":
            filename = "program.cpp"
        elif language == "java":
            filename = "Main.java"
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        filepath = os.path.join(tmp_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(code)
        
        return filepath
    
    def _create_container(self, language: str, tmp_dir: str) -> Any:
        """Create and start Docker container"""
        
        image = self.LANGUAGE_IMAGES[language]
        
        try:
            # Pull image if not available
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                self.client.images.pull(image)
        except Exception:
            pass  # Continue anyway, might fail at runtime but try
        
        container = self.client.containers.create(
            image,
            command="sleep 10",  # Keep container running for execution
            volumes={
                tmp_dir: {
                    "bind": "/code",
                    "mode": "ro"  # Read-only
                }
            },
            mem_limit=self.MEMORY_LIMIT,
            memswap_limit=self.MEMORY_LIMIT,
            cpu_quota=int(self.CPU_LIMIT * 100000),
            network_mode="none",  # No network access
            user="nobody",  # Non-root user
            stdin_open=True,
            stdout=True,
            stderr=True,
            remove=False
        )
        
        container.start()
        return container
    
    def _execute_in_container(
        self,
        container: Any,
        language: str,
        input_data: str
    ) -> str:
        """Execute command in container with input"""
        
        command = self.LANGUAGE_COMMANDS[language]
        if input_data:
            quoted_input = shlex.quote(input_data)
            command = f"printf %s {quoted_input} | ({command})"
        
        try:
            # Execute command with input and timeout
            exit_code, output = container.exec_run(
                ["sh", "-lc", command],
                stdout=True,
                stderr=False,
                timeout=self.EXEC_TIMEOUT_SECONDS,
                workdir="/code"
            )
            
            return output.decode("utf-8", errors="replace")
            
        except Exception as e:
            raise RuntimeError(f"Execution failed: {str(e)}")
    
    def execute_simple(
        self,
        code: str,
        language: str,
        input_data: str = ""
    ) -> ExecutionResult:
        """
        Simple execution without test cases.
        
        Args:
            code: Source code
            language: Programming language
            input_data: Input to pass to program
            
        Returns:
            ExecutionResult with status, stdout, stderr, execution_time_ms, exit_code
        """
        
        # Ensure Docker connection
        self._ensure_connected()
        
        container = None
        start_time = time.time()
        
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                self._write_code_file(code, language, tmp_dir)
                container = self._create_container(language, tmp_dir)
                
                output = self._execute_in_container(container, language, input_data)
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                return ExecutionResult(
                    status="success",
                    stdout=output,
                    stderr="",
                    execution_time_ms=execution_time_ms,
                    exit_code=0
                )
                
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                status="error",
                stdout="",
                stderr=str(e),
                execution_time_ms=execution_time_ms,
                exit_code=1
            )
            
        finally:
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove()
                except Exception:
                    pass
