from fastapi import APIRouter, HTTPException

from .schemas import (
    AnalyzeErrorResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeSuccessResponse,
    ExecuteErrorResponse,
    ExecuteRequest,
    ExecuteResponse,
    ExecuteSuccessResponse,
    OptimizeRequest,
    OptimizeResponse,
    OptimizeSuccessResponse,
)
from ..services.analyzer import CodeAnalyzer
from ..services.optimizer import CodeOptimizer
from ..services.local_executor import LocalSandboxExecutor
from ..services.sandbox_executor import DockerSandboxExecutor

router = APIRouter()
analyzer = CodeAnalyzer()
optimizer = CodeOptimizer()

# Initialize executor lazily
_executor = None
_executor_backend = None

def get_executor():
    """Get or initialize executor"""
    global _executor, _executor_backend
    if _executor is None:
        docker_executor = DockerSandboxExecutor()
        try:
            docker_executor._ensure_connected()
            _executor = docker_executor
            _executor_backend = "docker"
        except Exception:
            _executor = LocalSandboxExecutor()
            _executor_backend = "local"
    return _executor


@router.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/debug/info")
def debug_info() -> dict:
    """Debug information endpoint"""
    import sys
    
    return {
        "status": "ok",
        "python_version": sys.version,
        "analyzer_available": True,
        "optimizer_available": True,
        "docker_executor_initialized": _executor is not None,
        "execution_backend": _executor_backend or "uninitialized",
    }


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_code(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = analyzer.analyze(payload.code, payload.language)
    except Exception as exc:
        import traceback
        error_detail = f"Failed to analyze code: {str(exc)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to backend
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if result.status == "error":
        return AnalyzeErrorResponse(
            status="error",
            error_type=result.error_type,
            message=result.message,
            line=result.line,
        )

    return AnalyzeSuccessResponse(
        status="success",
        complexity=result.complexity,
        metrics=result.metrics,
        scores=result.scores,
        suggestions=result.suggestions,
        extra_issues=result.extra_issues,
    )


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_code(payload: OptimizeRequest) -> OptimizeResponse:
    try:
        result = optimizer.optimize(payload.code, payload.language)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to optimize code: {exc}") from exc

    if getattr(result, "status", "") == "error":
        return AnalyzeErrorResponse(
            status="error",
            error_type=result.error_type,
            message=result.message,
            line=result.line,
        )

    return OptimizeSuccessResponse(
        original_complexity=result.original_complexity,
        optimized_code=result.optimized_code,
        optimized_complexity=result.optimized_complexity,
        complexity_improved=result.complexity_improved,
        optimization_type=result.optimization_type,
        original_score=result.original_score,
        optimized_score=result.optimized_score,
        score_improvement=result.score_improvement,
        notes=result.notes,
    )


@router.post("/execute", response_model=ExecuteResponse)
def execute_code(payload: ExecuteRequest) -> ExecuteResponse:
    """
    Execute code in a Docker sandbox with test cases.
    
    Security measures:
    - Docker container isolation
    - Read-only filesystem
    - No network access
    - CPU and memory limits
    - 5-second execution timeout
    """
    try:
        # Get executor instance
        executor = get_executor()
        
        # Convert test cases to dict format for executor
        test_cases_data = [
            {"input": tc.input, "expected_output": tc.expected_output}
            for tc in payload.test_cases
        ]
        
        result = executor.execute_with_test_cases(
            payload.code,
            payload.language,
            test_cases_data
        )
        
        if result.get("status") == "error":
            return ExecuteErrorResponse(
                status="error",
                error=result.get("error", "Unknown error"),
                execution_time_ms=result.get("execution_time_ms", 0),
                results=[],
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
            )
        
        # Convert results to response format
        test_results = [
            {
                "input": r["input"],
                "expected_output": r["expected_output"],
                "actual_output": r["actual_output"],
                "passed": r["passed"],
                "error": r.get("error"),
            }
            for r in result.get("results", [])
        ]
        
        return ExecuteSuccessResponse(
            status="success",
            execution_time_ms=result.get("execution_time_ms", 0),
            results=test_results,
            stdout=result.get("stdout", ""),
            stderr=result.get("stderr", ""),
        )
        
    except Exception as exc:
        return ExecuteErrorResponse(
            status="error",
            error=f"Execution failed: {str(exc)}",
            execution_time_ms=0,
            results=[],
            stdout="",
            stderr=str(exc),
        )
