from typing import Literal

from pydantic import BaseModel, Field

SupportedLanguage = Literal["python", "c", "cpp", "java", "javascript", "go"]


class AnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to analyze")
    language: SupportedLanguage = Field(..., description="Programming language")


class MetricsResponse(BaseModel):
    lines_of_code: int = Field(..., ge=0)
    functions: int = Field(..., ge=0)
    loops: int = Field(..., ge=0)
    nesting_depth: int = Field(..., ge=0)
    cyclomatic_complexity: int = Field(..., ge=1)
    comment_ratio: float = Field(..., ge=0.0, le=1.0)


class ScoresResponse(BaseModel):
    readability: float = Field(..., ge=0, le=100)
    maintainability: float = Field(..., ge=0, le=100)
    efficiency: float = Field(..., ge=0, le=100)
    safety: float = Field(..., ge=0, le=100)
    overall: float = Field(..., ge=0, le=100)


class AnalyzeSuccessResponse(BaseModel):
    status: Literal["success"]
    complexity: str
    metrics: MetricsResponse
    scores: ScoresResponse
    suggestions: list[str]
    extra_issues: list[str] = Field(default_factory=list)


class AnalyzeErrorResponse(BaseModel):
    status: Literal["error"]
    error_type: Literal["syntax", "logic"]
    message: str = Field(..., min_length=1)
    line: int = Field(..., ge=1)


AnalyzeResponse = AnalyzeSuccessResponse | AnalyzeErrorResponse


class OptimizeRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to optimize")
    language: SupportedLanguage = Field(..., description="Programming language")


class OptimizeSuccessResponse(BaseModel):
    original_complexity: str
    optimized_code: str = Field(..., min_length=1)
    optimized_complexity: str
    complexity_improved: bool
    optimization_type: str
    original_score: float = Field(..., ge=0, le=100)
    optimized_score: float = Field(..., ge=0, le=100)
    score_improvement: str
    notes: str


OptimizeResponse = OptimizeSuccessResponse | AnalyzeErrorResponse


# ============================================
# EXECUTION & TEST CASES
# ============================================

class TestCase(BaseModel):
    """Single test case for code execution"""
    input: str = Field(default="", description="Input data for the test case")
    expected_output: str = Field(..., description="Expected output")


class ExecuteRequest(BaseModel):
    """Request to execute code in sandbox"""
    code: str = Field(..., min_length=1, description="Source code to execute")
    language: Literal["python", "c", "cpp", "java"] = Field(..., description="Programming language")
    test_cases: list[TestCase] = Field(default_factory=list, description="Test cases to run")


class TestCaseResultResponse(BaseModel):
    """Result of a single test case"""
    input: str
    expected_output: str
    actual_output: str
    passed: bool
    error: str | None = None


class ExecuteSuccessResponse(BaseModel):
    """Successful code execution response"""
    status: Literal["success"]
    execution_time_ms: float = Field(..., ge=0)
    results: list[TestCaseResultResponse] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""


class ExecuteErrorResponse(BaseModel):
    """Error during code execution"""
    status: Literal["error"]
    error: str = Field(..., min_length=1)
    execution_time_ms: float = Field(default=0, ge=0)
    results: list[TestCaseResultResponse] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""


ExecuteResponse = ExecuteSuccessResponse | ExecuteErrorResponse


