from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re

from .complexity_analyzer import ComplexityAnalyzer
from .feature_extractor import extract_features
from .io_compat import python_missing_print_warning
from .static_validator import StaticValidator, SyntaxValidationError

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None


@dataclass
class ScoreBreakdown:
    readability: float
    maintainability: float
    efficiency: float
    safety: float
    overall: float


@dataclass
class AnalyzeSuccessResult:
    status: str
    complexity: str
    metrics: dict[str, float | int]
    scores: dict[str, float]
    suggestions: list[str]
    extra_issues: list[str]


@dataclass
class AnalyzeErrorResult:
    status: str
    error_type: str
    message: str
    line: int


class CodeAnalyzer:
    def __init__(self):
        model_dir = Path(__file__).resolve().parents[1] / "ml" / "models"
        self.quality_model = self._load_model(model_dir / "quality_model.pkl")
        self.bug_model = self._load_model(model_dir / "bug_probability_model.pkl")
        self.validator = StaticValidator()
        self.complexity_analyzer = ComplexityAnalyzer()

    def _load_model(self, path: Path):
        if joblib is None or not path.exists():
            return None
        try:
            return joblib.load(path)
        except Exception:
            return None

    def analyze(self, code: str, language: str) -> AnalyzeSuccessResult | AnalyzeErrorResult:
        detected_language = self.validator.detect_language(code, language)

        try:
            program = self.validator.parse(code, detected_language)
        except SyntaxValidationError as exc:
            return AnalyzeErrorResult(
                status="error",
                error_type="syntax",
                message=str(exc),
                line=exc.line,
            )

        logic_issues = self.validator.run_logic_checks(program)
        fatal_issue = next((issue for issue in logic_issues if getattr(issue, "severity", "warning") == "error"), None)
        if fatal_issue is not None:
            return AnalyzeErrorResult(
                status="error",
                error_type="logic",
                message=fatal_issue.message,
                line=fatal_issue.line,
            )

        features = extract_features(code, detected_language)
        complexity = self.complexity_analyzer.compute(program.tree, code, program.source_bytes)

        metrics = {
            "lines_of_code": int(features["line_count"]),
            "functions": int(features["number_of_functions"]),
            "loops": int(features["number_of_loops"]),
            "nesting_depth": int(features["nested_loop_depth"]),
            "cyclomatic_complexity": int(features["cyclomatic_complexity"]),
            "comment_ratio": round(float(features["comment_ratio"]), 4),
        }

        scores = self._score_breakdown(code, complexity, metrics, features)
        suggestions = self._build_suggestions(code, detected_language, scores, complexity, metrics)
        warning_suggestions = [
            f"Line {issue.line}: {issue.message}"
            for issue in logic_issues
            if getattr(issue, "severity", "warning") == "warning"
        ]
        if warning_suggestions:
            suggestions = (warning_suggestions + suggestions)[:8]

        extra_issues = self._build_extra_issues(code, detected_language)

        return AnalyzeSuccessResult(
            status="success",
            complexity=complexity,
            metrics=metrics,
            scores={
                "readability": scores.readability,
                "maintainability": scores.maintainability,
                "efficiency": scores.efficiency,
                "safety": scores.safety,
                "overall": scores.overall,
            },
            suggestions=suggestions,
            extra_issues=extra_issues,
        )

    def _score_breakdown(
        self,
        code: str,
        complexity: str,
        metrics: dict[str, float | int],
        features: dict[str, float],
    ) -> ScoreBreakdown:
        readability = self._score_readability(code, float(metrics["comment_ratio"]))
        maintainability = self._score_maintainability(
            cyclomatic=float(metrics["cyclomatic_complexity"]),
            nesting_depth=float(metrics["nesting_depth"]),
        )
        efficiency = self._score_efficiency(complexity)
        safety = self._score_safety(code, features)

        overall = round(0.25 * readability + 0.25 * maintainability + 0.25 * efficiency + 0.25 * safety, 2)

        return ScoreBreakdown(
            readability=readability,
            maintainability=maintainability,
            efficiency=efficiency,
            safety=safety,
            overall=overall,
        )

    def _score_readability(self, code: str, comment_ratio: float) -> float:
        names = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", code)
        filtered = [n for n in names if n not in {"if", "for", "while", "return", "def", "class", "func"}]
        avg_name_len = sum(len(n) for n in filtered) / max(1, len(filtered))

        comment_score = min(comment_ratio / 0.15, 1.0) * 55
        naming_score = max(0.0, min(45.0, 45.0 - abs(avg_name_len - 8.0) * 4.0))
        return round(max(0.0, min(100.0, comment_score + naming_score)), 2)

    def _score_maintainability(self, cyclomatic: float, nesting_depth: float) -> float:
        value = 100.0 - (cyclomatic * 3.5) - (nesting_depth * 12.0)
        return round(max(0.0, min(100.0, value)), 2)

    def _score_efficiency(self, complexity: str) -> float:
        mapping = {
            "O(1)": 98.0,
            "O(log n)": 92.0,
            "O(n)": 82.0,
            "O(n log n)": 72.0,
            "O(n^2)": 50.0,
            "O(n^3)": 35.0,
            "O(2^n)": 15.0,
        }
        return mapping.get(complexity, 55.0)

    def _score_safety(self, code: str, features: dict[str, float]) -> float:
        lower = code.lower()
        safety = 82.0

        has_error_handling = any(token in lower for token in ("try", "catch", "except"))
        if has_error_handling:
            safety += 10.0

        risky_patterns = [r"\beval\s*\(", r"\bexec\s*\(", r"\bgoto\b", r"\bstrcpy\s*\("]
        risk_hits = sum(bool(re.search(pattern, lower)) for pattern in risky_patterns)
        safety -= risk_hits * 12.0

        if features["number_of_conditionals"] > 10:
            safety -= 6.0
        if features["nested_loop_depth"] >= 3:
            safety -= 8.0

        return round(max(0.0, min(100.0, safety)), 2)

    def _build_suggestions(
        self,
        code: str,
        language: str,
        scores: ScoreBreakdown,
        complexity: str,
        metrics: dict[str, float | int],
    ) -> list[str]:
        suggestions: list[str] = []

        if scores.readability < 60:
            suggestions.append("Improve naming consistency and add intent-focused comments.")
        if scores.maintainability < 65:
            suggestions.append("Reduce nesting depth and break large logic blocks into smaller functions.")
        if scores.efficiency < 65:
            suggestions.append("Optimize core algorithm to reduce time complexity.")
        if scores.safety < 65:
            suggestions.append("Add robust error handling and remove risky operations.")

        if complexity in {"O(n^2)", "O(n^3)", "O(2^n)"}:
            suggestions.append("Current complexity is expensive for scale; consider data-structure changes.")

        if float(metrics["comment_ratio"]) < 0.05:
            suggestions.append("Comment ratio is low; document non-obvious decisions.")

        if language == "python" and python_missing_print_warning(code):
            suggestions.append("Output not printed - add print statement.")

        if not suggestions:
            suggestions.append("Code quality looks healthy. Keep regression tests in place.")

        return suggestions[:6]

    def _build_extra_issues(self, code: str, language: str) -> list[str]:
        if language != "python":
            return []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        defined_functions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        called_functions = {
            call_name
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            for call_name in [self._extract_call_name(node.func)]
            if call_name
        }

        extra_issues: list[str] = []
        for name in sorted(defined_functions):
            if name not in called_functions:
                extra_issues.append(f"Function '{name}' is defined but never called.")

        has_input_call = "input" in called_functions
        has_print_call = "print" in called_functions
        has_main_block = self._has_python_main_block(tree)
        has_top_level_user_call = self._has_top_level_defined_function_call(tree, defined_functions)

        if defined_functions and not has_top_level_user_call:
            extra_issues.append("No execution entry point detected.")

        if not has_input_call and not has_print_call and not has_main_block:
            extra_issues.append("Program may not produce any output.")

        return extra_issues[:8]

    def _extract_call_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _has_python_main_block(self, tree: ast.Module) -> bool:
        for statement in tree.body:
            if not isinstance(statement, ast.If):
                continue
            test = statement.test
            if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
                continue
            left = test.left
            right = test.comparators[0]
            if (
                isinstance(test.ops[0], ast.Eq)
                and isinstance(left, ast.Name)
                and left.id == "__name__"
                and isinstance(right, ast.Constant)
                and right.value == "__main__"
            ):
                return True
        return False

    def _has_top_level_defined_function_call(self, tree: ast.Module, function_names: set[str]) -> bool:
        for statement in tree.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for node in ast.walk(statement):
                if not isinstance(node, ast.Call):
                    continue
                call_name = self._extract_call_name(node.func)
                if call_name in function_names:
                    return True
        return False
