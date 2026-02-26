def predict_quality(features: dict[str, int]) -> int:
    score = 90.0
    score -= features["loop_count"] * 2.0
    score -= features["branch_count"] * 1.5
    score -= features["max_loop_depth"] * 5.0
    score -= features["max_branch_depth"] * 3.0
    score -= max(features["line_count"] - 120, 0) * 0.05
    score += min(features["try_count"] * 2.0, 6.0)

    if features["function_count"] == 0:
        score -= 8.0
    if features["line_count"] < 8:
        score -= 5.0

    clamped = max(0, min(100, round(score)))
    return int(clamped)
