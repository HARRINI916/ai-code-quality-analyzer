def predict_complexity(features: dict[str, int]) -> str:
    loop_depth = features["max_loop_depth"]
    branch_depth = features["max_branch_depth"]
    calls = features["call_count"]

    if loop_depth >= 3:
        return "O(n^3)"
    if loop_depth == 2:
        return "O(n^2)"
    if loop_depth == 1 and branch_depth >= 2:
        return "O(n log n)"
    if loop_depth == 1 or calls > 10:
        return "O(n)"
    return "O(1)"
