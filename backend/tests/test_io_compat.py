from app.services.io_compat import (
    inject_python_execution_print_fallback,
    preserve_python_io_behavior,
    python_missing_print_warning,
)


def test_python_missing_print_warning_detects_return_only_code() -> None:
    code = "def f(x):\n    return x\n"
    assert python_missing_print_warning(code) is True


def test_preserve_python_io_behavior_keeps_input_and_print_contract() -> None:
    original = (
        "def f(nums):\n"
        "    return nums\n"
        "nums = list(map(int, input().split()))\n"
        "print(f(nums))\n"
    )
    optimized = "def f(nums):\n    return sorted(nums)\n"

    updated, notes = preserve_python_io_behavior(original, optimized)

    assert "input(" in updated
    assert "print(" in updated
    assert notes


def test_inject_python_execution_print_fallback_adds_main_footer() -> None:
    code = "def f(nums):\n    return nums\n"
    updated = inject_python_execution_print_fallback(code)

    assert "if __name__ == '__main__':" in updated
    assert "# --- Auto Execution Wrapper ---" in updated
    assert "nums = list(map(int, input().split()))" in updated
    assert "print(f(nums))" in updated


def test_inject_python_execution_print_fallback_reuses_original_input_pattern() -> None:
    code = "def three_sum(nums):\n    return nums\n"
    original = (
        "def three_sum(nums):\n"
        "    return nums\n"
        "nums = list(map(int, input().split()))\n"
        "print(three_sum(nums))\n"
    )

    updated = inject_python_execution_print_fallback(code, original_code=original)

    assert "nums = list(map(int, input().split()))" in updated
    assert "print(three_sum(nums))" in updated
