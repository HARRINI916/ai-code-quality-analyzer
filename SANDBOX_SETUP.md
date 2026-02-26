# Sandbox Execution Integration Guide

## Quick Start

### Prerequisites
1. Docker installed and running
2. Backend requirements installed (`docker >= 7.0.0`)

### Installation Steps

```bash
# 1. Update dependencies
cd backend
pip install --upgrade -r requirements.txt

# 2. Verify Docker
docker --version
docker ps

# 3. Start backend (if not already running)
python -m app.main:app --reload
```

### Frontend Components

The new execution feature is available through:

1. **TestCasePanel Component**
   - Located: `frontend/src/components/TestCasePanel.jsx`
   - Allows users to add/edit/delete test cases
   - Shows input and expected output fields

2. **ExecuteOutputPanel Component**
   - Located: `frontend/src/components/ExecuteOutputPanel.jsx`
   - Displays execution results
   - Shows pass/fail status for each test

### Using in Dashboard

To integrate into your Dashboard component:

```jsx
import TestCasePanel from "../components/TestCasePanel";
import ExecuteOutputPanel from "../components/ExecuteOutputPanel";
import { execute } from "../services/api";

// In your component state
const [testCases, setTestCases] = useState([]);
const [executionResult, setExecutionResult] = useState(null);
const [testRunning, setTestRunning] = useState(false);

// Handle test execution
async function handleRunTests() {
  setTestRunning(true);
  try {
    const result = await execute(code, language, testCases);
    setExecutionResult(result);
  } catch (err) {
    setExecutionResult({
      status: "error",
      error: err.message,
    });
  } finally {
    setTestRunning(false);
  }
}

// Render components
<TestCasePanel
  testCases={testCases}
  onTestCasesChange={setTestCases}
  onRunTests={handleRunTests}
  loading={testRunning}
  disabled={!code}
/>
<ExecuteOutputPanel
  executionResult={executionResult}
  loading={testRunning}
/>
```

## API Reference

### POST /execute Endpoint

**Request:**
```json
{
  "code": "print(int(input()) * 2)",
  "language": "python",
  "test_cases": [
    {
      "input": "5",
      "expected_output": "10"
    }
  ]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "execution_time_ms": 234.5,
  "results": [
    {
      "input": "5",
      "expected_output": "10",
      "actual_output": "10",
      "passed": true,
      "error": null
    }
  ],
  "stdout": "10\n",
  "stderr": ""
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Failed to connect to Docker daemon",
  "execution_time_ms": 0,
  "results": [],
  "stdout": "",
  "stderr": "..."
}
```

## Supported Languages

| Language | Min Version | Supported |
|----------|-------------|-----------|
| Python | 3.11 | ✅ Yes |
| C | GCC latest | ✅ Yes |
| C++ | G++ latest | ✅ Yes |
| Java | OpenJDK 17 | ✅ Yes |

## Security Features

✅ Docker container isolation
✅ Read-only filesystem
✅ CPU limit: 0.5 cores
✅ Memory limit: 128 MB
✅ No network access
✅ 5-second timeout
✅ Automatic cleanup

## Files Modified

### Backend
- `app/services/sandbox_executor.py` - New execution service
- `app/api/routes.py` - Added /execute endpoint
- `app/api/schemas.py` - Added test case schemas
- `requirements.txt` - Added docker dependency

### Frontend
- `src/services/api.js` - Added execute function
- `src/components/TestCasePanel.jsx` - Test input UI
- `src/components/ExecuteOutputPanel.jsx` - Results display

## Testing

### Test a Python execution
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"hello world\")",
    "language": "python",
    "test_cases": [{"input": "", "expected_output": "hello world"}]
  }'
```

### Test frontend
1. Open the app in browser
2. Select a language
3. Write code that reads input and prints output
4. Add test cases
5. Click "Run Tests"
6. View results

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker daemon not running | Start Docker Desktop or service |
| Container timeout | Optimize code (reduce complexity) |
| Memory limit exceeded | Reduce array sizes, use streaming |
| Compilation error | Check syntax, add includes |
| Tests never complete | Check for infinite loops |

---

For more details, see [SANDBOX_EXECUTION.md](SANDBOX_EXECUTION.md) and [SECURITY.md](SECURITY.md)
