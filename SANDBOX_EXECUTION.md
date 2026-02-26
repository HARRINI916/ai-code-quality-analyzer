# Sandbox Code Execution System

## Overview

The AI Code Quality Analyzer now includes a **secure Docker-based code execution sandbox** that allows users to run and test code safely in isolated containers.

## Features

✅ **Secure Execution**
- Docker container isolation
- Read-only filesystem
- CPU and memory limits
- Network access disabled
- 5-second execution timeout
- Automatic cleanup

✅ **Test Case Support**
- Multiple test cases per execution
- Input/output validation
- Pass/fail results
- Detailed error reporting

✅ **Multi-Language Support**
- Python 3.11
- C (GCC)
- C++ (G++)
- Java (OpenJDK 17)

✅ **Real-time Feedback**
- Execution time tracking
- Standard output capture
- Error output capture
- Test result aggregation

## Architecture

### Execution Flow

```
Frontend (Test Case Input)
        ↓
API Endpoint (/execute)
        ↓
DockerSandboxExecutor
        ↓
Create Temp File
        ↓
Launch Docker Container
        ↓
Execute Code with Input
        ↓
Capture Output
        ↓
Cleanup Container
        ↓
Return Results to Frontend
```

### Docker Container Configuration

Each execution runs in an isolated container with:

| Setting | Value | Reason |
|---------|-------|--------|
| Memory Limit | 128 MB | Prevent memory exhaustion |
| CPU Limit | 0.5 cores | Prevent CPU hogging |
| Network Mode | None | Disable internet access |
| Filesystem | Read-only | Prevent file modifications |
| User | nobody | Non-root for security |
| Timeout | 5 seconds | Prevent infinite loops |

## Usage

### Backend Setup

1. **Install Docker** (if not already installed)
   ```bash
   # macOS
   brew install docker
   
   # Windows/Linux
   # Download from https://www.docker.com/products/docker-desktop
   ```

2. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt  # includes docker>=7.0.0
   ```

3. **Verify Docker Connection**
   ```bash
   docker --version
   docker run hello-world
   ```

### API Usage

**Example: Python Test Case Execution**

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = int(input())\nprint(x * 2)",
    "language": "python",
    "test_cases": [
      {
        "input": "5",
        "expected_output": "10"
      },
      {
        "input": "7",
        "expected_output": "14"
      }
    ]
  }'
```

**Response:**
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
    },
    {
      "input": "7",
      "expected_output": "14",
      "actual_output": "14",
      "passed": true,
      "error": null
    }
  ],
  "stdout": "10\n14\n",
  "stderr": ""
}
```

### Frontend Usage

1. **Write Code** in the editor
2. **Add Test Cases** in the Test Case Panel
   - Enter input data
   - Enter expected output
3. **Click Run Tests**
4. **View Results**
   - Pass/fail status for each test
   - Execution time
   - Actual vs expected output
   - Error messages if any

## Test Case Examples

### Python

**Code:**
```python
def sum_numbers(n):
    return sum(range(1, n + 1))

n = int(input())
print(sum_numbers(n))
```

**Test Cases:**
```json
[
  {"input": "5", "expected_output": "15"},
  {"input": "10", "expected_output": "55"},
  {"input": "100", "expected_output": "5050"}
]
```

### C

**Code:**
```c
#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    
    int sum = 0;
    for (int i = 1; i <= n; i++) {
        sum += i;
    }
    
    printf("%d", sum);
    return 0;
}
```

**Test Cases:**
```json
[
  {"input": "5", "expected_output": "15"},
  {"input": "10", "expected_output": "55"}
]
```

### C++

**Code:**
```cpp
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int sum = 0;
    for (int i = 1; i <= n; i++) {
        sum += i;
    }
    
    cout << sum;
    return 0;
}
```

**Test Cases:**
```json
[
  {"input": "3", "expected_output": "6"},
  {"input": "4", "expected_output": "10"}
]
```

### Java

**Code:**
```java
public class Main {
    public static void main(String[] args) {
        int n = Integer.parseInt(args[0]);
        
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum += i;
        }
        
        System.out.print(sum);
    }
}
```

**Test Cases:**
```json
[
  {"input": "5", "expected_output": "15"},
  {"input": "10", "expected_output": "55"}
]
```

## Performance Characteristics

### Timing

| Operation | Time |
|-----------|------|
| First execution (image pull) | 3-10s |
| Subsequent execution | 500-2000ms |
| Container startup | 200-500ms |
| Code compilation (C/C++) | 100-500ms |
| Code execution | 50-500ms |

### Resource Usage

| Resource | Usage |
|----------|-------|
| Memory per execution | ~50-100 MB |
| Disk space for images | ~500 MB (all images) |
| Network bandwidth | ~0 (isolated) |
| Process overhead | 1 container per execution |

## Error Handling

### Common Errors

**Docker Not Running**
```
Error: Failed to connect to Docker daemon: ...
```
**Solution:** Start Docker daemon
```bash
docker daemon &
```

**Code Compilation Error** (C/C++)
```
error: 'printf' undeclared
```
**Solution:** Include necessary headers
```c
#include <stdio.h>
```

**Timeout Error**
```
Error: Execution failed: timeout
```
**Solution:** Optimize code for performance (reduce nested loops, use efficient algorithms)

**Memory Limit Exceeded**
```
Error: Container killed: memory limit exceeded
```
**Solution:** Reduce memory usage (avoid large arrays, use generators)

**Syntax Error in Test Case**
```
Error: Invalid test case format
```
**Solution:** Ensure expected_output is a string

## Implementation Details

### Core Classes

**DockerSandboxExecutor** (`sandbox_executor.py`)
- Main executor class
- Manages Docker container lifecycle
- Handles test case execution
- Captures output and errors

**Key Methods:**
```python
execute_with_test_cases(code, language, test_cases) -> dict
execute_simple(code, language, input_data) -> ExecutionResult
```

### API Endpoint

**POST /execute**
```python
@router.post("/execute", response_model=ExecuteResponse)
def execute_code(payload: ExecuteRequest) -> ExecuteResponse:
    # Executes code in Docker sandbox
    result = executor.execute_with_test_cases(
        payload.code,
        payload.language,
        test_cases_data
    )
    return result
```

### Frontend Components

**TestCasePanel.jsx**
- Input/output test case management
- Add/edit/delete test cases
- Run tests button

**ExecuteOutputPanel.jsx**
- Display test results
- Show pass/fail status
- Display stdout/stderr
- Show execution time

## Security

### Sandbox Protections

1. **Isolation**: Each execution runs in separate container
2. **Resource Limits**: CPU capped, memory capped
3. **Network Disabled**: No internet access allowed
4. **Read-Only FS**: Cannot modify files
5. **Timeout**: Execution fails after 5 seconds
6. **Auto-Cleanup**: Containers deleted after execution
7. **Non-Root User**: Code runs as 'nobody' user

### What Cannot Be Done

- ❌ Access host filesystem
- ❌ Make network requests
- ❌ Fork child processes (limited)
- ❌ Access environment variables
- ❌ Modify other containers
- ❌ Restart container
- ❌ Install packages

## Troubleshooting

### Issue: Docker images not downloading

**Cause:** Network connectivity issue

**Solution:**
```bash
docker pull python:3.11-slim
docker pull gcc:latest
docker pull openjdk:17-slim
```

### Issue: Slow execution

**Cause:** Docker overhead on first run

**Solution:** Pre-pull images
```bash
docker pull python:3.11-slim && \
docker pull gcc:latest && \
docker pull openjdk:17-slim
```

### Issue: Tests timing out

**Cause:** Code is inefficient (nested loops, etc)

**Solution:** Optimize algorithm complexity

### Issue: Memory limit exceeded

**Cause:** Allocating too much memory

**Solution:** Use generators, streaming instead of loading all data

## Future Enhancements

1. **Custom Timeout**: Allow per-request timeout configuration
2. **Execution History**: Track previous executions
3. **Code Profiling**: Show execution time per line
4. **Memory Profiling**: Show memory usage per operation
5. **Performance Optimization**: Suggest optimizations based on profile
6. **Debugging Integration**: Step-through debugging
7. **CI/CD Integration**: Run tests in GitHub Actions
8. **Benchmark Mode**: Compare performance across languages

## Files Modified/Created

### Backend
- [app/services/sandbox_executor.py](../backend/app/services/sandbox_executor.py) - Docker executor
- [app/api/routes.py](../backend/app/api/routes.py) - /execute endpoint
- [app/api/schemas.py](../backend/app/api/schemas.py) - Test case schemas
- [requirements.txt](../backend/requirements.txt) - Added docker dependency

### Frontend  
- [src/services/api.js](../frontend/src/services/api.js) - Added execute function
- [src/components/TestCasePanel.jsx](../frontend/src/components/TestCasePanel.jsx) - Test input UI
- [src/components/ExecuteOutputPanel.jsx](../frontend/src/components/ExecuteOutputPanel.jsx) - Results display

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Container Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

**Last Updated:** February 22, 2026
**Version:** 1.0
