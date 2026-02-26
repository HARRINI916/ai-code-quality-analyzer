from __future__ import annotations

from dataclasses import dataclass
import re

from .base_parser import BaseParser, ParsedCode

try:
    from tree_sitter_languages import get_parser as get_tree_sitter_parser
except Exception:  # pragma: no cover - optional dependency at runtime
    get_tree_sitter_parser = None


@dataclass(frozen=True)
class NodeRules:
    function_tokens: tuple[str, ...]
    loop_tokens: tuple[str, ...]
    conditional_tokens: tuple[str, ...]
    comment_tokens: tuple[str, ...] = ("comment",)


class TreeSitterLanguageParser(BaseParser):
    def __init__(self, language: str, rules: NodeRules):
        self.language = language
        self.rules = rules

    def parse(self, code: str) -> ParsedCode:
        if not code.strip():
            raise ValueError("Code input is empty.")
        if get_tree_sitter_parser is None:
            return self._fallback_parse(code)

        parser = get_tree_sitter_parser(self.language)
        tree = parser.parse(code.encode("utf-8"))

        if tree.root_node.has_error:
            raise ValueError(f"Syntax error detected in {self.language} code.")

        lines_of_code = len([line for line in code.splitlines() if line.strip()])
        if lines_of_code == 0:
            lines_of_code = 1

        function_count = 0
        loop_count = 0
        conditional_count = 0
        comment_count = 0
        max_loop_depth = 0

        def contains_token(node_type: str, tokens: tuple[str, ...]) -> bool:
            return any(token in node_type for token in tokens)

        def visit(node, current_loop_depth: int) -> None:
            nonlocal function_count, loop_count, conditional_count, comment_count, max_loop_depth

            node_type = node.type
            next_depth = current_loop_depth

            if contains_token(node_type, self.rules.function_tokens):
                function_count += 1

            if contains_token(node_type, self.rules.loop_tokens):
                loop_count += 1
                next_depth += 1
                max_loop_depth = max(max_loop_depth, next_depth)

            if contains_token(node_type, self.rules.conditional_tokens):
                conditional_count += 1

            if contains_token(node_type, self.rules.comment_tokens):
                comment_count += 1

            for child in node.children:
                visit(child, next_depth)

        visit(tree.root_node, 0)

        cyclomatic = max(1, 1 + loop_count + conditional_count)
        comment_ratio = round(comment_count / lines_of_code, 4)

        return ParsedCode(
            line_count=lines_of_code,
            number_of_loops=loop_count,
            nested_loop_depth=max_loop_depth,
            number_of_functions=function_count,
            number_of_conditionals=conditional_count,
            cyclomatic_complexity=cyclomatic,
            comment_ratio=comment_ratio,
        )

    def _fallback_parse(self, code: str) -> ParsedCode:
        if self.language == "python":
            try:
                compile(code, "<code>", "exec")
            except SyntaxError as exc:
                raise ValueError(f"Syntax error detected in python code: {exc.msg}") from exc

        lines = [line for line in code.splitlines() if line.strip()]
        text = code.lower()
        lines_of_code = len(lines) if lines else 1

        loop_patterns = [r"\bfor\b", r"\bwhile\b", r"\bdo\b", r"\brange\b"]
        cond_patterns = [r"\bif\b", r"\belse if\b", r"\bswitch\b", r"\bcase\b"]
        function_patterns = [r"\bdef\b", r"\bfunc\b", r"\bfunction\b", r"\b[A-Za-z_]\w*\s*\([^)]*\)\s*\{"]
        comment_markers = ("#", "//", "/*")

        loop_count = sum(len(re.findall(pattern, text)) for pattern in loop_patterns)
        conditional_count = sum(len(re.findall(pattern, text)) for pattern in cond_patterns)
        function_count = sum(len(re.findall(pattern, text)) for pattern in function_patterns)
        comment_count = sum(1 for line in lines if line.strip().startswith(comment_markers))

        nested_depth = 2 if loop_count >= 2 else 1 if loop_count == 1 else 0
        cyclomatic = max(1, 1 + loop_count + conditional_count)
        comment_ratio = round(comment_count / lines_of_code, 4)

        return ParsedCode(
            line_count=lines_of_code,
            number_of_loops=loop_count,
            nested_loop_depth=nested_depth,
            number_of_functions=function_count,
            number_of_conditionals=conditional_count,
            cyclomatic_complexity=cyclomatic,
            comment_ratio=comment_ratio,
        )
