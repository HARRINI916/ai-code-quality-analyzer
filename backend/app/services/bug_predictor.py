def predict_bug_probability(features: dict[str, int]) -> float:
    probability = 0.12
    probability += features["loop_count"] * 0.03
    probability += features["branch_count"] * 0.025
    probability += features["max_branch_depth"] * 0.04
    probability += features["max_loop_depth"] * 0.05
    probability += max(features["line_count"] - 80, 0) * 0.0015
    probability -= min(features["try_count"] * 0.02, 0.08)

    return round(max(0.0, min(1.0, probability)), 3)
