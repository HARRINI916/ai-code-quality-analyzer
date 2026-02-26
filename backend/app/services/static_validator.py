from __future__ import annotations

import re
from dataclasses import dataclass

try:
    from tree_sitter_languages import get_parser as get_tree_sitter_parser
except Exception:  # pragma: no cover - optional dependency at runtime
    get_tree_sitter_parser = None

SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java", "javascript", "go"}


class SyntaxValidationError(ValueError):
    def __init__(self, message: str, line: int):
        super().__init__(message)
        self.line = line


@dataclass(frozen=True)
class LogicIssue:
    message: str
    line: int
    severity: str = "warning"


@dataclass(frozen=True)
class ParsedProgram:
    language: str
    code: str
    source_bytes: bytes
    tree: object | None


class StaticValidator:
    def detect_language(self, code: str, requested_language: str | None = None) -> str:
        if requested_language:
            normalized = requested_language.strip().lower()
            if normalized in SUPPORTED_LANGUAGES:
                return normalized

        text = code.strip()
        if text.startswith("package main") or "func " in text:
            return "go"
        if "#include" in text:
            if "std::" in text or "cout" in text:
                return "cpp"
            return "c"
        if "public class" in text:
            return "java"
        if "function " in text or "=>" in text or "console." in text:
            return "javascript"
        return "python"

    def parse(self, code: str, language: str) -> ParsedProgram:
        if not code.strip():
            raise SyntaxValidationError("Code input is empty.", 1)

        if get_tree_sitter_parser is None:
            self._fallback_syntax_validate(code, language)
            return ParsedProgram(language=language, code=code, source_bytes=code.encode("utf-8"), tree=None)

        parser = get_tree_sitter_parser(language)
        source_bytes = code.encode("utf-8")
        tree = parser.parse(source_bytes)

        if tree.root_node.has_error:
            line = self._first_error_line(tree.root_node)
            raise SyntaxValidationError("Invalid syntax", line)

        if self._contains_tree_errors(tree.root_node):
            line = self._first_error_line(tree.root_node)
            raise SyntaxValidationError("Invalid syntax", line)

        return ParsedProgram(language=language, code=code, source_bytes=source_bytes, tree=tree)

    def run_logic_checks(self, program: ParsedProgram) -> list[LogicIssue]:
        issues: list[LogicIssue] = []

        issue_line = self._unreachable_after_return_line(program)
        if issue_line is not None:
            issues.append(LogicIssue("Unreachable code detected after return statement.", issue_line, "warning"))

        issue_line = self._infinite_loop_line(program)
        if issue_line is not None:
            issues.append(LogicIssue("Potential infinite loop detected: loop condition is always true without break.", issue_line, "error"))

        unused_variables = self._find_unused_variables(program.code)
        if unused_variables:
            names = ", ".join(unused_variables[:5])
            issues.append(LogicIssue(f"Unused variables detected: {names}.", 1, "warning"))

        issue_line = self._empty_catch_line(program)
        if issue_line is not None:
            issues.append(LogicIssue("Empty catch/except block detected.", issue_line, "warning"))

        issue_line = self._missing_return_line(program)
        if issue_line is not None:
            issues.append(LogicIssue("Possible missing return path in function with conditional returns.", issue_line, "warning"))

        return issues

    def _fallback_syntax_validate(self, code: str, language: str) -> None:
        if language == "python":
            try:
                compile(code, "<submitted>", "exec")
            except SyntaxError as exc:
                line = exc.lineno or 1
                raise SyntaxValidationError(f"Invalid syntax: {exc.msg}", int(line)) from exc

        if code.count("{") != code.count("}"):
            line = self._line_for_token_mismatch(code, "{", "}")
            raise SyntaxValidationError("Invalid syntax: unbalanced braces.", line)
        if code.count("(") != code.count(")"):
            line = self._line_for_token_mismatch(code, "(", ")")
            raise SyntaxValidationError("Invalid syntax: unbalanced parentheses.", line)

    def _line_for_token_mismatch(self, code: str, left: str, right: str) -> int:
        balance = 0
        for idx, line in enumerate(code.splitlines(), start=1):
            balance += line.count(left)
            balance -= line.count(right)
            if balance < 0:
                return idx
        return max(1, len(code.splitlines()))

    def _contains_tree_errors(self, node) -> bool:
        if node.type in {"ERROR", "MISSING"}:
            return True
        return any(self._contains_tree_errors(child) for child in node.children)

    def _first_error_line(self, node) -> int:
        if node.type in {"ERROR", "MISSING"}:
            return int(node.start_point[0]) + 1
        for child in node.children:
            line = self._first_error_line(child)
            if line:
                return line
        return int(node.start_point[0]) + 1

    def _is_return_node(self, node) -> bool:
        return "return" in node.type

    def _is_statement_node(self, node) -> bool:
        node_type = node.type
        if node_type in {"}", ")", "]", ":", ";", ","}:
            return False
        return node_type.endswith("statement") or node_type.endswith("declaration") or node_type in {
            "expression_statement",
            "assignment",
            "call",
            "return_statement",
            "throw_statement",
            "break_statement",
            "continue_statement",
            "pass_statement",
        }

    def _unreachable_after_return_line(self, program: ParsedProgram) -> int | None:
        if program.tree is None:
            return None

        def visit(node) -> int | None:
            found_return = False
            for child in node.children:
                if found_return and self._is_statement_node(child):
                    return int(child.start_point[0]) + 1
                if self._is_return_node(child):
                    found_return = True
                child_line = visit(child)
                if child_line is not None:
                    return child_line
            return None

        return visit(program.tree.root_node)

    def _node_text(self, node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")

    def _contains_break(self, node) -> bool:
        if "break" in node.type:
            return True
        return any(self._contains_break(child) for child in node.children)

    def _is_always_true_condition(self, text: str) -> bool:
        normalized = re.sub(r"\s+", "", text)
        return normalized in {"true", "(true)", "1", "(1)"}

    def _infinite_loop_line(self, program: ParsedProgram) -> int | None:
        if program.tree is None:
            for idx, line in enumerate(program.code.splitlines(), start=1):
                normalized = re.sub(r"\s+", "", line.lower())
                if "whiletrue:" in normalized or "while(true)" in normalized or "for(;;)" in normalized:
                    if "break" not in program.code:
                        return idx
            return None

        source = program.source_bytes

        def visit(node) -> int | None:
            if "while_statement" in node.type:
                condition = node.child_by_field_name("condition")
                body = node.child_by_field_name("body")
                if condition is not None and body is not None:
                    condition_text = self._node_text(condition, source)
                    if self._is_always_true_condition(condition_text) and not self._contains_break(body):
                        return int(node.start_point[0]) + 1

            if "for_statement" in node.type:
                condition = node.child_by_field_name("condition")
                body = node.child_by_field_name("body")
                if body is not None:
                    if condition is None and not self._contains_break(body):
                        return int(node.start_point[0]) + 1

            for child in node.children:
                found = visit(child)
                if found is not None:
                    return found
            return None

        return visit(program.tree.root_node)

    def _find_unused_variables(self, code: str) -> list[str]:
        declared: set[str] = set()

        patterns = [
            r"\b(?:var|let|const)\s+([A-Za-z_]\w*)",
            r"\b(?:int|float|double|long|short|char|bool|String|auto|var)\s+([A-Za-z_]\w*)",
            r"\b([A-Za-z_]\w*)\s*:=" ,
            r"^\s*([A-Za-z_]\w*)\s*=\s*[^=]",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, code, flags=re.MULTILINE):
                declared.add(match.group(1))

        ignore = {"i", "j", "k", "n", "m", "tmp", "temp"}
        candidates = [name for name in declared if name not in ignore and not name.startswith("_")]

        unused: list[str] = []
        for name in sorted(candidates):
            occurrences = re.findall(rf"\b{re.escape(name)}\b", code)
            if len(occurrences) <= 1:
                unused.append(name)
        return unused

    def _empty_catch_line(self, program: ParsedProgram) -> int | None:
        code = program.code
        language = program.language

        if language == "python":
            for match in re.finditer(r"except[^\n]*:\s*(pass|\.\.\.)", code):
                return code[: match.start()].count("\n") + 1

        patterns = [
            r"catch\s*\([^)]*\)\s*\{\s*\}",
            r"catch\s*\([^)]*\)\s*\{\s*/\*.*?\*/\s*\}",
            r"catch\s*\([^)]*\)\s*\{\s*//[^\n]*\s*\}",
        ]
        for pattern in patterns:
            match = re.search(pattern, code, flags=re.DOTALL)
            if match:
                return code[: match.start()].count("\n") + 1
        return None

    def _missing_return_line(self, program: ParsedProgram) -> int | None:
        if program.tree is None:
            return None

        source = program.source_bytes

        def is_function_node(node_type: str) -> bool:
            return any(token in node_type for token in ("function", "method_declaration", "constructor_declaration"))

        def has_return(node) -> bool:
            if "return" in node.type:
                return True
            return any(has_return(child) for child in node.children)

        def visit(node) -> int | None:
            node_type = node.type
            if is_function_node(node_type):
                body = node.child_by_field_name("body")
                if body is not None:
                    body_text = self._node_text(body, source)
                    has_conditional = "if" in body_text
                    if has_conditional and has_return(body):
                        stripped = re.sub(r"\s+", " ", body_text).strip()
                        if stripped and "return" in stripped and not re.search(r"return\b[^;\n]*[;\n]\s*\}?\s*$", stripped):
                            return int(node.start_point[0]) + 1
            for child in node.children:
                child_issue = visit(child)
                if child_issue is not None:
                    return child_issue
            return None

        return visit(program.tree.root_node)
