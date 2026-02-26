from app.services.output_comparator import compare_outputs


def test_compare_outputs_list_of_lists_order_insensitive() -> None:
    expected = "[[-1, -1, 2], [-1, 0, 1]]"
    actual = "[[1, -1, 0], [2, -1, -1]]"

    passed, normalized_expected, normalized_actual = compare_outputs(expected, actual)

    assert passed is True
    assert normalized_expected == normalized_actual


def test_compare_outputs_empty_lists() -> None:
    passed, normalized_expected, normalized_actual = compare_outputs("[]", "[]")

    assert passed is True
    assert normalized_expected == "[]"
    assert normalized_actual == "[]"


def test_compare_outputs_single_triplet_with_order_difference() -> None:
    passed, normalized_expected, normalized_actual = compare_outputs("[[-1, 0, 1]]", "[[1, -1, 0]]")

    assert passed is True
    assert normalized_expected == normalized_actual


def test_compare_outputs_parse_error_falls_back_to_string() -> None:
    passed, normalized_expected, normalized_actual = compare_outputs("hello", "hello")

    assert passed is True
    assert normalized_expected == "hello"
    assert normalized_actual == "hello"


def test_compare_outputs_detects_real_mismatch() -> None:
    passed, _, _ = compare_outputs("[[-1, 0, 1]]", "[[-1, 0, 2]]")

    assert passed is False
