def score(quality: float, complexity: float, bugs: float):
    return {"score": (quality - complexity - bugs)}
