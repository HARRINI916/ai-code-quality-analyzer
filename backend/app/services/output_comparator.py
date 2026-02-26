from __future__ import annotations

import ast
from typing import Any


def _is_list_of_lists(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, list) for item in value)


def _normalize_list_of_lists(value: list[list[Any]]) -> list[list[Any]]:
    normalized_inner = [sorted(inner, key=repr) for inner in value]
    return sorted(normalized_inner, key=repr)


def _parse_maybe_literal(raw: str) -> tuple[bool, Any]:
    text = (raw or "").strip()
    if text == "":
        return True, ""
    try:
        return True, ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return False, text


def compare_outputs(expected_output: str, actual_output: str) -> tuple[bool, str, str]:
    """
    Compare expected and actual outputs with structural normalization for list outputs.

    Rules:
    - Safely parse with ast.literal_eval when possible
    - If both values are list-of-lists, normalize:
      - Sort each inner list
      - Sort outer list
    - Compare parsed values structurally
    - Fall back to trimmed string comparison when parsing is unavailable

    Returns:
      (passed, normalized_expected_text, normalized_actual_text)
    """
    expected_parsed_ok, expected_value = _parse_maybe_literal(expected_output)
    actual_parsed_ok, actual_value = _parse_maybe_literal(actual_output)

    if expected_parsed_ok and actual_parsed_ok:
        if _is_list_of_lists(expected_value) and _is_list_of_lists(actual_value):
            expected_value = _normalize_list_of_lists(expected_value)
            actual_value = _normalize_list_of_lists(actual_value)

        passed = expected_value == actual_value
        return passed, repr(expected_value), repr(actual_value)

    expected_text = (expected_output or "").strip()
    actual_text = (actual_output or "").strip()
    return expected_text == actual_text, expected_text, actual_text
