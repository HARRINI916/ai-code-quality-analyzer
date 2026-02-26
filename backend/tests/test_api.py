from fastapi.testclient import TestClient
import os
from unittest.mock import patch

from app.main import app
from app.services.execution_service import CodeExecutionService


client = TestClient(app)


def test_analyze_returns_syntax_error_for_invalid_code() -> None:
    response = client.post(
        "/analyze",
        json={"language": "python", "code": "def broken(:\n    return 1"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "error"
    assert payload["error_type"] == "syntax"
    assert isinstance(payload["line"], int)
    assert "scores" not in payload


def test_analyze_returns_logic_error_for_infinite_loop() -> None:
    response = client.post(
        "/analyze",
        json={"language": "python", "code": "def f():\n    while True:\n        x = 1\n"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "error"
    assert payload["error_type"] == "logic"
    assert isinstance(payload["line"], int)
    assert "scores" not in payload


def test_analyze_returns_success_with_new_contract() -> None:
    response = client.post(
        "/analyze",
        json={
            "language": "python",
            "code": "def sum_positive(items):\n    total = 0\n    for item in items:\n        if item > 0:\n            total += item\n    return total\n",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert payload["complexity"].startswith("O(")
    assert payload["metrics"]["lines_of_code"] >= 1
    assert payload["metrics"]["comment_ratio"] >= 0
    assert payload["scores"]["overall"] >= 0
    assert payload["scores"]["overall"] <= 100
    assert "extra_issues" in payload
    assert isinstance(payload["extra_issues"], list)


def test_analyze_reports_unused_function_and_missing_entrypoint() -> None:
    response = client.post(
        "/analyze",
        json={
            "language": "python",
            "code": "def three_sum_n3(nums):\n    return []\n",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert "Function 'three_sum_n3' is defined but never called." in payload["extra_issues"]
    assert "No execution entry point detected." in payload["extra_issues"]


def test_analyze_does_not_report_unused_for_called_function() -> None:
    response = client.post(
        "/analyze",
        json={
            "language": "python",
            "code": "def main():\n    print('ok')\n\nmain()\n",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert "Function 'main' is defined but never called." not in payload["extra_issues"]
    assert "No execution entry point detected." not in payload["extra_issues"]


def test_optimize_returns_error_for_invalid_input() -> None:
    response = client.post(
        "/optimize",
        json={"language": "python", "code": "def broken(:\n    return 1"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "error"
    assert payload["error_type"] == "syntax"
    assert isinstance(payload["line"], int)


def test_optimize_returns_optimized_payload() -> None:
    response = client.post(
        "/optimize",
        json={
            "language": "python",
            "code": "def sum_positive(items):\n    total = 0\n    for item in items:\n        if item > 0:\n            total += item\n    return total\n",
        },
    )
    payload = response.json()

    assert response.status_code == 200
    assert "original_complexity" in payload
    assert "optimized_code" in payload
    assert payload["optimized_complexity"].startswith("O(")
    assert isinstance(payload["complexity_improved"], bool)
    assert "optimization_type" in payload
    assert "original_score" in payload
    assert "optimized_score" in payload
    assert "score_improvement" in payload
    assert "notes" in payload


def test_optimize_does_not_return_worse_complexity() -> None:
    response = client.post(
        "/optimize",
        json={
            "language": "python",
            "code": "def f(a,b):\n    out=[]\n    for x in a:\n        for y in b:\n            if x == y:\n                out.append(x)\n    return out\n",
        },
    )
    payload = response.json()
    order = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]

    assert response.status_code == 200
    assert order.index(payload["optimized_complexity"]) <= order.index(payload["original_complexity"])


def test_optimize_three_sum_bruteforce_to_quadratic() -> None:
    code = """def three_sum(nums):
    result = []
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplet = sorted([nums[i], nums[j], nums[k]])
                    if triplet not in result:
                        result.append(triplet)
    return result
"""
    response = client.post("/optimize", json={"language": "python", "code": code})
    payload = response.json()

    assert response.status_code == 200
    assert payload["original_complexity"] == "O(n^3)"
    assert payload["optimized_complexity"] == "O(n^2)"
    assert payload["complexity_improved"] is True
    assert payload["optimization_type"] == "algorithmic improvement"


def test_execution_payload_template_matches_requested_format() -> None:
    service = CodeExecutionService()
    payload = service.build_payload("python", "print('Hello')")

    assert payload["model"] == "gpt-4o-mini"
    assert payload["temperature"] == 0
    assert payload["messages"][0]["role"] == "system"
    assert "ONLY the exact output" in payload["messages"][0]["content"]
    assert payload["messages"][1]["role"] == "user"
    assert "Language: python" in payload["messages"][1]["content"]
    assert "Code:\nprint('Hello')" in payload["messages"][1]["content"]


def test_execute_returns_error_when_api_key_missing() -> None:
    previous = os.environ.pop("OPENAI_API_KEY", None)
    try:
        response = client.post("/execute", json={"language": "python", "code": "print('x')"})
    finally:
        if previous is not None:
            os.environ["OPENAI_API_KEY"] = previous

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "error"
    assert "OPENAI_API_KEY is not set" in payload["message"]


def test_execute_route_returns_output() -> None:
    previous = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "test-key"

    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{\"choices\":[{\"message\":{\"content\":\"3\"}}]}'

    try:
        with patch("urllib.request.urlopen", return_value=_FakeResponse()):
            response = client.post("/execute", json={"language": "python", "code": "print(1+2)"})
    finally:
        if previous is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = previous

    payload = response.json()
    assert response.status_code == 200
    assert payload["output"] == "3"
