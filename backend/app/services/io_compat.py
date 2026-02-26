from __future__ import annotations

import ast
import re


def _safe_parse_python(code: str) -> ast.AST | None:
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def _first_function_name(tree: ast.AST | None) -> str | None:
    if tree is None:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node.name
    return None


def _has_call(tree: ast.AST | None, fn_name: str) -> bool:
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == fn_name:
            return True
    return False


def _has_print(tree: ast.AST | None) -> bool:
    return _has_call(tree, "print")


def _has_input(tree: ast.AST | None) -> bool:
    return _has_call(tree, "input")


def _has_return(tree: ast.AST | None) -> bool:
    if tree is None:
        return False
    return any(isinstance(node, ast.Return) for node in ast.walk(tree))


def _contains_main_guard(code: str) -> bool:
    return "__name__ == '__main__'" in code or '__name__ == "__main__"' in code


def _extract_lines_with_token(code: str, token_pattern: str) -> list[str]:
    lines: list[str] = []
    pattern = re.compile(token_pattern)
    for line in code.splitlines():
        if pattern.search(line):
            stripped = line.rstrip()
            if stripped:
                lines.append(stripped)
    return lines


def _extract_original_print_call_args(original_code: str, function_name: str) -> str | None:
    pattern = re.compile(rf"print\s*\(\s*{re.escape(function_name)}\s*\((.*?)\)\s*\)")
    match = pattern.search(original_code)
    if not match:
        return None
    return match.group(1).strip() or None


def _extract_input_assignment_from_original(original_code: str) -> tuple[str | None, str | None]:
    for line in original_code.splitlines():
        if "input(" not in line:
            continue
        stripped = line.strip()
        m = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", stripped)
        if m:
            return m.group(1), stripped
    return None, None


def _function_arg_names(tree: ast.AST | None, function_name: str) -> list[str]:
    if tree is None:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return [arg.arg for arg in node.args.args]
    return []


def python_missing_print_warning(code: str) -> bool:
    tree = _safe_parse_python(code)
    if tree is None:
        return False
    return _has_return(tree) and not _has_print(tree)


def inject_python_execution_print_fallback(code: str, original_code: str | None = None) -> str:
    """
    Inject a minimal executable footer for Python when code returns values
    but does not print output.
    """
    tree = _safe_parse_python(code)
    if tree is None:
        return code
    if _has_print(tree) or not _has_return(tree):
        return code

    fn_name = _first_function_name(tree)
    if not fn_name:
        return code

    if _contains_main_guard(code):
        return code

    source_for_pattern = original_code or ""
    arg_names = _function_arg_names(tree, fn_name)
    input_var, input_assignment_line = _extract_input_assignment_from_original(source_for_pattern)
    original_call_args = _extract_original_print_call_args(source_for_pattern, fn_name)

    if original_call_args:
        call_expr = f"{fn_name}({original_call_args})"
    elif input_var and len(arg_names) <= 1:
        call_expr = f"{fn_name}({input_var})"
    elif len(arg_names) <= 1:
        call_expr = f"{fn_name}(nums)"
    else:
        call_expr = f"{fn_name}(*nums)"

    wrapper_lines = [
        "",
        "# --- Auto Execution Wrapper ---",
        "if __name__ == '__main__':",
    ]
    if input_assignment_line:
        wrapper_lines.append(f"    {input_assignment_line}")
    else:
        wrapper_lines.append("    nums = list(map(int, input().split()))")
    wrapper_lines.append(f"    print({call_expr})")

    candidate = code.rstrip() + "\n" + "\n".join(wrapper_lines) + "\n"
    # Validate syntax after injection.
    return candidate if _safe_parse_python(candidate) is not None else code


def preserve_python_io_behavior(original_code: str, optimized_code: str) -> tuple[str, list[str]]:
    """
    Preserve original input/print behavior in optimized Python code.
    """
    notes: list[str] = []
    original_tree = _safe_parse_python(original_code)
    optimized_tree = _safe_parse_python(optimized_code)
    if optimized_tree is None:
        return optimized_code, notes

    original_has_input = _has_input(original_tree)
    original_has_print = _has_print(original_tree)
    optimized_has_input = _has_input(optimized_tree)
    optimized_has_print = _has_print(optimized_tree)

    extra_lines: list[str] = []
    optimized_text = optimized_code

    if original_has_input and not optimized_has_input:
        for line in _extract_lines_with_token(original_code, r"\binput\s*\("):
            if line not in optimized_text:
                extra_lines.append(line)
        if extra_lines:
            notes.append("Preserved input() behavior from original code.")

    if original_has_print and not optimized_has_print:
        original_print_lines = _extract_lines_with_token(original_code, r"\bprint\s*\(")
        appended = False
        for line in original_print_lines:
            if line not in optimized_text:
                extra_lines.append(line)
                appended = True
        if appended:
            notes.append("Preserved print() behavior from original code.")

    if extra_lines:
        optimized_text = optimized_code.rstrip() + "\n\n" + "\n".join(extra_lines) + "\n"

    # Final safety net: if code still returns values without printing, add a fallback print footer.
    if python_missing_print_warning(optimized_text):
        injected = inject_python_execution_print_fallback(optimized_text, original_code=original_code)
        if injected != optimized_text:
            optimized_text = injected
            notes.append("Added executable print fallback for return-only code.")

    return optimized_text, notes
