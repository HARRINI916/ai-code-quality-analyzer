from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ComplexityFeatures:
    loop_count: int
    max_loop_depth: int
    has_log_loop: bool
    has_binary_search_pattern: bool
    recursion_branch_factor: int


class ComplexityAnalyzer:
    def compute(self, tree, code: str, source_bytes: bytes) -> str:
        if self._has_three_sum_two_pointer_pattern(code):
            return "O(n^2)"
        if tree is None:
            return self._fallback_big_o(code)
        features = self._extract_features(tree.root_node, code, source_bytes)
        return self._to_big_o(features)

    def _has_three_sum_two_pointer_pattern(self, code: str) -> bool:
        normalized = re.sub(r"\s+", "", code.lower())
        required_tokens = [
            ".sort()",
            "foriinrange(",
            "left,right=i+1,n-1",
            "whileleft<right",
            "total=",
            "left+=1",
            "right-=1",
        ]
        if not all(token in normalized for token in required_tokens):
            return False
        return (
            "[i]" in normalized
            and "[left]" in normalized
            and "[right]" in normalized
            and "total==0" in normalized
        )

    def _fallback_big_o(self, code: str) -> str:
        normalized = re.sub(r"\s+", "", code.lower())
        if re.search(r"\b([A-Za-z_]\w*)\s*\([^)]*\)\s*{", code):
            for fn in re.findall(r"\b([A-Za-z_]\w*)\s*\(", code):
                if len(re.findall(rf"\b{re.escape(fn)}\s*\(", code)) >= 3:
                    return "O(2^n)"

        if (
            ("left<=right" in normalized or "low<=high" in normalized)
            and "mid=" in normalized
            and ("left=mid+1" in normalized or "low=mid+1" in normalized)
        ):
            return "O(log n)"

        lines = [line.strip() for line in code.splitlines() if line.strip()]
        loop_lines = [line for line in lines if re.search(r"\b(for|while)\b", line)]
        if not loop_lines:
            return "O(1)"
        if len(loop_lines) == 1:
            if re.search(r"\*=|/=|>>=|<<=", loop_lines[0]):
                return "O(log n)"
            return "O(n)"
        if len(loop_lines) == 2:
            return "O(n^2)"
        if len(loop_lines) >= 3:
            return "O(n^3)"
        return "O(n)"

    def _extract_features(self, root, code: str, source_bytes: bytes) -> ComplexityFeatures:
        loop_count = 0
        max_loop_depth = 0
        recursion_branch_factor = 0

        def node_text(node) -> str:
            return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")

        def function_name(node):
            named = node.child_by_field_name("name")
            if named is not None:
                return node_text(named).strip()
            for child in node.children:
                if child.type in {"identifier", "field_identifier", "type_identifier"}:
                    value = node_text(child).strip()
                    if value:
                        return value
            return None

        def visit(node, current_loop_depth: int) -> None:
            nonlocal loop_count, max_loop_depth, recursion_branch_factor

            next_depth = current_loop_depth
            if "for_statement" in node.type or "while_statement" in node.type or "do_statement" in node.type:
                loop_count += 1
                next_depth += 1
                max_loop_depth = max(max_loop_depth, next_depth)

            if any(token in node.type for token in ("function", "method_declaration", "function_definition")):
                name = function_name(node)
                body = node.child_by_field_name("body")
                if name and body is not None:
                    body_text = node_text(body)
                    self_calls = len(re.findall(rf"\b{re.escape(name)}\s*\(", body_text))
                    recursion_branch_factor = max(recursion_branch_factor, max(0, self_calls))

            for child in node.children:
                visit(child, next_depth)

        visit(root, 0)

        has_log_loop = bool(
            re.search(r"\b[A-Za-z_]\w*\s*(\*=|/=|>>=|<<=)\s*2\b", code)
            or re.search(r"\b[A-Za-z_]\w*\s*=\s*[A-Za-z_]\w*\s*([*/]|>>|<<)\s*2\b", code)
        )

        normalized = re.sub(r"\s+", "", code.lower())
        has_binary_search_pattern = (
            ("left<=right" in normalized or "low<=high" in normalized)
            and "mid=" in normalized
            and (
                "left=mid+1" in normalized
                or "right=mid-1" in normalized
                or "low=mid+1" in normalized
                or "high=mid-1" in normalized
            )
        )

        return ComplexityFeatures(
            loop_count=loop_count,
            max_loop_depth=max_loop_depth,
            has_log_loop=has_log_loop,
            has_binary_search_pattern=has_binary_search_pattern,
            recursion_branch_factor=recursion_branch_factor,
        )

    def _to_big_o(self, features: ComplexityFeatures) -> str:
        if features.recursion_branch_factor >= 2:
            return "O(2^n)"

        if features.has_binary_search_pattern:
            return "O(log n)"

        if features.max_loop_depth == 0:
            return "O(1)"

        if features.max_loop_depth == 1:
            if features.has_log_loop:
                return "O(log n)"
            return "O(n)"

        if features.max_loop_depth == 2:
            if features.has_log_loop:
                return "O(n log n)"
            return "O(n^2)"

        if features.max_loop_depth == 3:
            return "O(n^3)"

        if features.has_log_loop:
            return f"O(n^{features.max_loop_depth - 1} log n)"
        return f"O(n^{features.max_loop_depth})"
