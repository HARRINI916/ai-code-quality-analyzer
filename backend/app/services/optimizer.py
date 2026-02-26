from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from .analyzer import AnalyzeErrorResult, AnalyzeSuccessResult, CodeAnalyzer
from .io_compat import preserve_python_io_behavior


@dataclass
class OptimizeSuccessResult:
    original_complexity: str
    optimized_code: str
    optimized_complexity: str
    complexity_improved: bool
    optimization_type: str
    original_score: float
    optimized_score: float
    score_improvement: str
    notes: str


class CodeOptimizer:
    def __init__(self):
        self.analyzer = CodeAnalyzer()

    def optimize(self, code: str, language: str) -> OptimizeSuccessResult | AnalyzeErrorResult:
        original = self.analyzer.analyze(code, language)
        if isinstance(original, AnalyzeErrorResult):
            return original

        original_rank = self._complexity_rank(original.complexity)

        candidate_pool: list[tuple[str, list[str]]] = []
        llm_candidate, llm_notes = self._generate_candidate(code, language)
        candidate_pool.append((self._strip_code_fence(llm_candidate), llm_notes))

        fallback_candidate, fallback_notes = self._rule_based_optimize(code, language)
        candidate_pool.append((self._strip_code_fence(fallback_candidate), fallback_notes))

        best_code = code
        best_result = original
        best_notes = ["Complexity could not be improved safely without changing semantics. Returned original code."]
        best_rank = original_rank

        for candidate_code, candidate_notes in candidate_pool:
            candidate_code, io_notes = self._ensure_io_compatibility(code, candidate_code, language)
            if io_notes:
                candidate_notes = candidate_notes + io_notes

            if candidate_code.strip() == code.strip():
                continue

            analyzed = self.analyzer.analyze(candidate_code, language)
            if isinstance(analyzed, AnalyzeErrorResult):
                continue

            analyzed_rank = self._complexity_rank(analyzed.complexity)

            if analyzed_rank < best_rank:
                best_code = candidate_code
                best_result = analyzed
                best_notes = candidate_notes
                best_rank = analyzed_rank

        complexity_improved = best_rank < original_rank
        if not complexity_improved:
            best_code = code
            best_result = original
            if not best_notes:
                best_notes = ["No mathematically better complexity rewrite was found for this snippet."]

        score_diff = round(best_result.scores["overall"] - original.scores["overall"], 2)
        optimization_type = "algorithmic improvement" if complexity_improved else "no complexity improvement"
        notes = self._merge_notes(original, best_result, best_notes, complexity_improved)

        return OptimizeSuccessResult(
            original_complexity=original.complexity,
            optimized_code=best_code,
            optimized_complexity=best_result.complexity,
            complexity_improved=complexity_improved,
            optimization_type=optimization_type,
            original_score=round(original.scores["overall"], 2),
            optimized_score=round(best_result.scores["overall"], 2),
            score_improvement=f"{score_diff:+g}",
            notes=notes,
        )

    def _ensure_io_compatibility(self, original_code: str, candidate_code: str, language: str) -> tuple[str, list[str]]:
        if language != "python":
            return candidate_code, []
        return preserve_python_io_behavior(original_code, candidate_code)

    def _complexity_rank(self, value: str) -> int:
        order = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]
        try:
            return order.index(value)
        except ValueError:
            return len(order)

    def _generate_candidate(self, code: str, language: str) -> tuple[str, list[str]]:
        llm_code = self._llm_optimize(code, language)
        if llm_code:
            return llm_code, ["AI refactor applied with complexity-reduction objective."]
        return self._rule_based_optimize(code, language)

    def _llm_optimize(self, code: str, language: str) -> str | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        model = os.getenv("OPENAI_OPTIMIZER_MODEL", "gpt-4.1-mini")
        system_prompt = (
            "You are an algorithm optimization engine. Preserve functionality exactly. "
            "Preserve input/output behavior exactly (input parsing and printed output contract). "
            "Detect brute-force nested-loop patterns and replace with known optimal strategies "
            "(for example Three Sum two-pointer after sorting). "
            "Actively reduce time complexity where possible. "
            "If complexity cannot be improved, keep behavior-equivalent structure. "
            "Return only valid executable code, no markdown, no commentary."
        )
        user_prompt = (
            f"Language: {language}\n"
            "Refactor this code to optimize complexity and readability:\n\n"
            f"{code}"
        )

        payload = {
            "model": model,
            "temperature": 0.0,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                body = response.read().decode("utf-8")
            parsed = json.loads(body)
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            return None

        text = parsed.get("output_text")
        if isinstance(text, str) and text.strip():
            return text.strip()

        collected: list[str] = []
        for item in parsed.get("output", []):
            for content in item.get("content", []):
                content_text = content.get("text")
                if isinstance(content_text, str):
                    collected.append(content_text)

        joined = "\n".join(collected).strip()
        return joined or None

    def _rule_based_optimize(self, code: str, language: str) -> tuple[str, list[str]]:
        optimized = code
        notes: list[str] = []

        if language == "python":
            optimized, changed = self._optimize_python_three_sum_bruteforce(optimized)
            if changed:
                notes.append("Replaced triple nested brute-force Three Sum with sorted two-pointer strategy.")

            optimized, changed = self._optimize_python_membership_loop(optimized)
            if changed:
                notes.append("Nested loop replaced with set lookup to reduce O(n^2) scans.")

            optimized, changed = self._optimize_python_repeated_membership_check(optimized)
            if changed:
                notes.append("Repeated linear membership checks replaced with precomputed set lookup.")

            optimized, changed = self._optimize_python_recursive_fib(optimized)
            if changed:
                notes.append("Two-branch recursion optimized with memoization.")

            optimized, changed = self._remove_python_redundant_conditions(optimized)
            if changed:
                notes.append("Removed redundant conditional branches.")

        optimized = self._normalize_blank_lines(optimized)
        return optimized, notes

    def _optimize_python_three_sum_bruteforce(self, code: str) -> tuple[str, bool]:
        # Detect common O(n^3) Three Sum brute-force pattern with duplicate filtering.
        header = re.search(r"^\s*def\s+([A-Za-z_]\w*)\s*\(\s*([A-Za-z_]\w*)", code, flags=re.MULTILINE)
        if not header:
            return code, False

        fn_name = header.group(1)
        arr_name = header.group(2)

        result_init = re.search(r"^\s*([A-Za-z_]\w*)\s*=\s*\[\s*\]\s*$", code, flags=re.MULTILINE)
        result_return = re.search(r"^\s*return\s+([A-Za-z_]\w*)\s*$", code, flags=re.MULTILINE)
        result_var = result_init.group(1) if result_init else (result_return.group(1) if result_return else "result")

        has_three_range_loops = (
            "for i in range" in code
            and "for j in range" in code
            and "for k in range" in code
        )
        has_sum_eq_zero = bool(
            re.search(
                rf"{re.escape(arr_name)}\s*\[\s*i\s*\]\s*\+\s*{re.escape(arr_name)}\s*\[\s*j\s*\]\s*\+\s*{re.escape(arr_name)}\s*\[\s*k\s*\]\s*==\s*0",
                code,
            )
        )
        has_duplicate_filter = (
            "triplet not in" in code
            or bool(re.search(rf"\bif\s+\w+\s+not\s+in\s+{re.escape(result_var)}\s*:", code))
        )

        if not (has_three_range_loops and has_sum_eq_zero and has_duplicate_filter):
            return code, False

        replacement = (
            f"def {fn_name}({arr_name}):\n"
            f"    {arr_name}.sort()\n"
            f"    {result_var} = []\n"
            f"    n = len({arr_name})\n"
            f"    for i in range(n - 2):\n"
            f"        if i > 0 and {arr_name}[i] == {arr_name}[i - 1]:\n"
            f"            continue\n"
            f"        left, right = i + 1, n - 1\n"
            f"        while left < right:\n"
            f"            total = {arr_name}[i] + {arr_name}[left] + {arr_name}[right]\n"
            f"            if total == 0:\n"
            f"                {result_var}.append([{arr_name}[i], {arr_name}[left], {arr_name}[right]])\n"
            f"                left += 1\n"
            f"                right -= 1\n"
            f"                while left < right and {arr_name}[left] == {arr_name}[left - 1]:\n"
            f"                    left += 1\n"
            f"                while left < right and {arr_name}[right] == {arr_name}[right + 1]:\n"
            f"                    right -= 1\n"
            f"            elif total < 0:\n"
            f"                left += 1\n"
            f"            else:\n"
            f"                right -= 1\n"
            f"    return {result_var}\n"
        )

        return replacement, True

    def _optimize_python_membership_loop(self, code: str) -> tuple[str, bool]:
        lines = code.splitlines()
        for idx in range(len(lines) - 3):
            first = lines[idx]
            second = lines[idx + 1]
            third = lines[idx + 2]
            fourth = lines[idx + 3]

            m1 = re.match(r"^(\s*)for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)\s*:\s*$", first)
            m2 = re.match(r"^(\s*)for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)\s*:\s*$", second)
            if not m1 or not m2:
                continue

            indent1, item_var, left_arr = m1.groups()
            indent2, right_var, right_arr = m2.groups()
            if len(indent2) <= len(indent1):
                continue

            m3 = re.match(rf"^\s*if\s+{re.escape(item_var)}\s*==\s*{re.escape(right_var)}\s*:\s*$", third)
            m4 = re.match(rf"^\s*([A-Za-z_]\w*)\.append\(\s*{re.escape(item_var)}\s*\)\s*$", fourth)
            if not m3 or not m4:
                continue

            out_arr = m4.group(1)
            replacement = [
                f"{indent1}{right_arr}_set = set({right_arr})",
                f"{indent1}for {item_var} in {left_arr}:",
                f"{indent1}    if {item_var} in {right_arr}_set:",
                f"{indent1}        {out_arr}.append({item_var})",
            ]
            new_lines = lines[:idx] + replacement + lines[idx + 4 :]
            return "\n".join(new_lines) + "\n", True

        return code, False

    def _optimize_python_repeated_membership_check(self, code: str) -> tuple[str, bool]:
        lines = code.splitlines()
        for idx in range(len(lines) - 1):
            loop = lines[idx]
            cond = lines[idx + 1]

            loop_match = re.match(r"^(\s*)for\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)\s*:\s*$", loop)
            if not loop_match:
                continue
            indent, iter_var, _iterable = loop_match.groups()

            cond_match = re.match(
                rf"^\s*if\s+{re.escape(iter_var)}\s+in\s+([A-Za-z_]\w+)\s*:\s*$",
                cond,
            )
            if not cond_match:
                continue

            lookup_list = cond_match.group(1)
            if lookup_list.endswith("_set"):
                continue
            set_line = f"{indent}{lookup_list}_set = set({lookup_list})"
            new_cond = re.sub(rf"\bin\s+{re.escape(lookup_list)}\b", f"in {lookup_list}_set", cond)

            if set_line.strip() in code:
                continue

            new_lines = lines[:idx] + [set_line, loop, new_cond] + lines[idx + 2 :]
            return "\n".join(new_lines) + "\n", True

        return code, False

    def _optimize_python_recursive_fib(self, code: str) -> tuple[str, bool]:
        func_match = re.search(
            r"def\s+([A-Za-z_]\w*)\s*\(\s*n\s*\)\s*:\s*\n"
            r"\s*if\s+n\s*<=\s*1\s*:\s*\n"
            r"\s*return\s+n\s*\n"
            r"\s*return\s+\1\(n-1\)\s*\+\s*\1\(n-2\)",
            code,
            flags=re.MULTILINE,
        )
        if not func_match:
            return code, False

        name = func_match.group(1)
        replacement = (
            "from functools import lru_cache\n\n"
            f"@lru_cache(maxsize=None)\n"
            f"def {name}(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            f"    return {name}(n-1) + {name}(n-2)"
        )
        return replacement + "\n", True

    def _remove_python_redundant_conditions(self, code: str) -> tuple[str, bool]:
        updated = re.sub(
            r"if\s+True\s*:\s*\n(\s+)(.+)",
            lambda m: f"{m.group(1)}{m.group(2)}",
            code,
            flags=re.MULTILINE,
        )
        return updated, updated != code

    def _normalize_blank_lines(self, code: str) -> str:
        lines = code.splitlines()
        cleaned: list[str] = []
        blank_count = 0
        for line in lines:
            if line.strip():
                blank_count = 0
                cleaned.append(line.rstrip())
            else:
                blank_count += 1
                if blank_count <= 1:
                    cleaned.append("")
        text = "\n".join(cleaned).strip()
        return f"{text}\n" if text else "\n"

    def _strip_code_fence(self, code: str) -> str:
        stripped = code.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z0-9_+-]*\n", "", stripped)
            stripped = re.sub(r"\n```$", "", stripped)
        return stripped.strip() + "\n"

    def _merge_notes(
        self,
        original: AnalyzeSuccessResult,
        optimized: AnalyzeSuccessResult,
        raw_notes: list[str],
        complexity_improved: bool,
    ) -> str:
        notes: list[str] = []
        seen = set()

        for item in raw_notes:
            if item and item not in seen:
                seen.add(item)
                notes.append(item)

        if complexity_improved:
            notes.append(f"Complexity reduced from {original.complexity} to {optimized.complexity}.")
        elif original.complexity == optimized.complexity and not raw_notes:
            notes.append("Complexity cannot be improved safely without changing program semantics.")

        if optimized.scores["overall"] > original.scores["overall"]:
            notes.append("Overall score increased after optimization.")

        return " ".join(notes).strip()
