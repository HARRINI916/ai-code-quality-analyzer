from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .io_compat import inject_python_execution_print_fallback
from .output_comparator import compare_outputs


@dataclass
class ExecutionResult:
    status: str
    stdout: str
    stderr: str
    execution_time_ms: float
    exit_code: int


class LocalSandboxExecutor:
    """
    Fallback executor when Docker is unavailable.

    This is less isolated than Docker and should be treated as a compatibility mode.
    """

    EXEC_TIMEOUT_SECONDS = 5
    SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}

    def execute_with_test_cases(self, code: str, language: str, test_cases: list[dict]) -> dict:
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}",
                "execution_time_ms": 0,
                "results": [],
                "stdout": "",
                "stderr": "",
            }

        start = time.time()
        results = []
        total_stdout = ""
        total_stderr = ""

        try:
            if not test_cases:
                simple = self.execute_simple(code, language, "")
                if simple.status == "error":
                    return {
                        "status": "error",
                        "error": simple.stderr or "Execution failed",
                        "execution_time_ms": simple.execution_time_ms,
                        "results": [],
                        "stdout": simple.stdout,
                        "stderr": simple.stderr,
                    }
                return {
                    "status": "success",
                    "execution_time_ms": simple.execution_time_ms,
                    "results": [],
                    "stdout": simple.stdout,
                    "stderr": simple.stderr,
                }

            for tc in test_cases:
                one = self._run_one(code, language, tc.get("input", ""), tc.get("expected_output", ""))
                results.append(one)
                total_stdout += one.get("actual_output", "")
                if one.get("error"):
                    total_stderr += one["error"] + "\n"

            return {
                "status": "success",
                "execution_time_ms": (time.time() - start) * 1000,
                "results": results,
                "stdout": total_stdout,
                "stderr": total_stderr,
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc),
                "execution_time_ms": (time.time() - start) * 1000,
                "results": results,
                "stdout": total_stdout,
                "stderr": total_stderr,
            }

    def execute_simple(self, code: str, language: str, input_data: str = "") -> ExecutionResult:
        start = time.time()
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                workdir = Path(tmp_dir)
                self._write_code_file(code, language, workdir)
                compile_cmd, run_cmd = self._commands_for(language, workdir)

                if compile_cmd:
                    compiled = self._run_cmd(compile_cmd, workdir, "")
                    if compiled.returncode != 0:
                        return ExecutionResult(
                            status="error",
                            stdout=compiled.stdout,
                            stderr=compiled.stderr,
                            execution_time_ms=(time.time() - start) * 1000,
                            exit_code=compiled.returncode,
                        )

                ran = self._run_cmd(run_cmd, workdir, input_data)
                status = "success" if ran.returncode == 0 else "error"
                return ExecutionResult(
                    status=status,
                    stdout=ran.stdout,
                    stderr=ran.stderr,
                    execution_time_ms=(time.time() - start) * 1000,
                    exit_code=ran.returncode,
                )
        except Exception as exc:
            return ExecutionResult(
                status="error",
                stdout="",
                stderr=str(exc),
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=1,
            )

    def _run_one(self, code: str, language: str, input_data: str, expected_output: str) -> dict:
        result = self.execute_simple(code, language, input_data)
        # Fallback: if Python code produced no stdout, try a safe print-wrapper execution.
        if (
            language == "python"
            and result.status == "success"
            and not result.stdout.strip()
            and expected_output.strip()
        ):
            fallback_code = inject_python_execution_print_fallback(code, original_code=code)
            if fallback_code != code:
                retry = self.execute_simple(fallback_code, language, input_data)
                if retry.status == "success" and retry.stdout.strip():
                    result = retry

        if result.status == "error":
            return {
                "input": input_data,
                "expected_output": expected_output,
                "actual_output": result.stdout,
                "passed": False,
                "error": result.stderr or "Execution failed",
            }
        passed, normalized_expected, normalized_actual = compare_outputs(expected_output, result.stdout)
        return {
            "input": input_data,
            "expected_output": normalized_expected,
            "actual_output": normalized_actual,
            "passed": passed,
            "error": None,
        }

    def _write_code_file(self, code: str, language: str, workdir: Path) -> None:
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

        (workdir / filename).write_text(code, encoding="utf-8")

    def _commands_for(self, language: str, workdir: Path) -> tuple[Optional[list[str]], list[str]]:
        if language == "python":
            return None, ["python", "script.py"]
        if language == "c":
            self._require_binary("gcc")
            exe_name = "program.exe" if os.name == "nt" else "program"
            return ["gcc", "program.c", "-O2", "-o", exe_name], [str(workdir / exe_name)]
        if language == "cpp":
            self._require_binary("g++")
            exe_name = "program.exe" if os.name == "nt" else "program"
            return ["g++", "program.cpp", "-O2", "-o", exe_name], [str(workdir / exe_name)]
        if language == "java":
            self._require_binary("javac")
            self._require_binary("java")
            return ["javac", "Main.java"], ["java", "Main"]
        raise ValueError(f"Unsupported language: {language}")

    def _run_cmd(self, cmd: list[str], workdir: Path, input_data: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=str(workdir),
            input=input_data,
            text=True,
            capture_output=True,
            timeout=self.EXEC_TIMEOUT_SECONDS,
            shell=False,
        )

    def _require_binary(self, name: str) -> None:
        if shutil.which(name) is None:
            raise RuntimeError(f"Required compiler/runtime not found: {name}")
