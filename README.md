# CodePulse AI

Multi-language AI code quality and complexity analyzer.  
Current implementation in this repository uses `React + Vite + Monaco` frontend and `FastAPI` backend with Tree-sitter parser integration and ML-model fallback behavior.

## Features

- Analyze source code for: Python, C, C++, Java, JavaScript, and Go.
- Unified parser output via language parser abstraction.
- `POST /analyze` API with:
  - `complexity`
  - `metrics` (LOC, functions, loops, nesting depth, cyclomatic complexity, comment ratio)
  - `scores` (readability, maintainability, efficiency, safety, overall)
  - `suggestions`
- `POST /optimize` API to generate optimized code on demand and return optimization comparison metadata.
- Monaco editor dashboard with language dropdown, loading state, dark mode, and responsive cards.
- Docker Compose stack including backend, frontend, PostgreSQL, and Redis.

## Project Structure

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/api/schemas.py`
- `backend/app/parsers/`
- `backend/app/services/feature_extractor.py`
- `backend/app/services/analyzer.py`
- `backend/app/database/models.py`
- `backend/app/ml/models/`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/components/`

## Local Run

### 1) Backend

```powershell
cd C:\Users\priya\Desktop\ai-code-quality-analyzer
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

API docs: `http://localhost:8000/docs`

Optional AI optimizer environment:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_OPTIMIZER_MODEL="gpt-4.1-mini"
```

If `OPENAI_API_KEY` is not set, `/optimize` uses deterministic rule-based optimizations.

### 2) Frontend

```powershell
cd C:\Users\priya\Desktop\ai-code-quality-analyzer\frontend
npm install
npm run dev
```

App: `http://localhost:5173`

## API Contract

### Request

`POST /analyze`

```json
{
  "code": "def add(a,b): return a+b",
  "language": "python"
}
```

### Response

```json
{
  "status": "success",
  "complexity": "O(n)",
  "metrics": {
    "lines_of_code": 5,
    "functions": 1,
    "loops": 1,
    "nesting_depth": 1,
    "cyclomatic_complexity": 2,
    "comment_ratio": 0.1
  },
  "scores": {
    "readability": 78,
    "maintainability": 80,
    "efficiency": 82,
    "safety": 88,
    "overall": 82
  },
  "suggestions": [
    "Code metrics look healthy. Maintain quality with regression tests."
  ]
}
```

`POST /optimize`

```json
{
  "original_complexity": "O(n^2)",
  "optimized_code": "def optimized(...):\n    ...\n",
  "optimized_complexity": "O(n)",
  "complexity_improved": true,
  "optimization_type": "algorithmic improvement",
  "original_score": 65,
  "optimized_score": 85,
  "score_improvement": "+20",
  "notes": "Nested loop replaced with hashmap/set lookup."
}
```

The optimizer re-analyzes generated code and guarantees optimized complexity is never worse than original; otherwise it returns the original code with explanatory `notes`.

## Docker

```powershell
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`
