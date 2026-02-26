# Security & System Restrictions

## Code Execution Policy

**Status: ENABLED WITH SANDBOX ISOLATION**

The AI Code Quality Analyzer now supports **secure code execution** using Docker container isolation. Code execution is protected by multiple layers of security.

### Execution Architecture

The system uses **Docker container sandbox** for all code execution:

```
User Code → Temporary File → Docker Container (Isolated)
              ↓
         [Security Layers]
         • Read-only filesystem
         • No network access
         • CPU limit (0.5 cores)
         • Memory limit (128MB)
         • Execution timeout (5 seconds)
         ↓
         Container Cleanup (Auto-deleted)
```

### What the System Does

✅ **Allowed Operations:**

**1. Static Code Analysis** (`POST /analyze`)
   - Syntax validation
   - Complexity analysis (Big-O notation)
   - Code metrics (LOC, functions, loops, nesting depth, cyclomatic complexity)
   - Quality scoring (readability, maintainability, efficiency, safety)
   - Best practice suggestions

**2. Code Optimization** (`POST /optimize`)
   - Generates optimized versions of submitted code
   - Analyzes algorithmic complexity improvements
   - Provides optimization rationale and notes

**3. Secure Code Execution** (`POST /execute`)
   - Runs user-submitted code in isolated Docker containers
   - Executes test cases with input/output validation
   - Captures stdout and stderr safely
   - Returns pass/fail results for each test case

### What the System Does NOT Do

❌ **Blocked Operations:**
- Execute code directly on the host machine
- Use `exec()` or `eval()` functions
- Make system calls or access OS directly
- Grant network access to containers
- Read or write files outside sandbox
- Access system resources without limits
- Persist container state after execution

### Container Security Configuration

Each container runs with these restrictions:

```yaml
Memory Limit: 128 MB
CPU Limit: 0.5 cores (50%)
Network Mode: None (isolated)
Filesystem: Read-only (except /tmp)
User: nobody (non-root)
Timeout: 5 seconds per execution
```

### API Endpoints

#### Available Endpoints

**1. POST /health**
- Health check endpoint
- Returns: `{"status": "healthy"}`

**2. POST /analyze**
- Analyzes submitted code statically (no execution)
- Returns: complexity, metrics, scores, suggestions

```json
{
  "input": {
    "code": "user_code_string",
    "language": "python|javascript|java|cpp|c|go"
  },
  "output": {
    "status": "success",
    "complexity": "O(n^2)",
    "metrics": {...},
    "scores": {...},
    "suggestions": [...]
  }
}
```

**3. POST /optimize**
- Generates optimized code version
- Returns: optimized code with complexity metrics

```json
{
  "input": {
    "code": "user_code_string",
    "language": "python"
  },
  "output": {
    "original_complexity": "O(n^2)",
    "optimized_code": "optimized_code_string",
    "optimized_complexity": "O(n log n)",
    "complexity_improved": true,
    "notes": "Optimization details"
  }
}
```

**4. POST /execute** (NEW - SANDBOXED)
- Executes code with test cases in isolated Docker container
- Supported languages: python, c, cpp, java
- Returns: test results with pass/fail status

```json
{
  "input": {
    "code": "user_code",
    "language": "python",
    "test_cases": [
      {
        "input": "5 3",
        "expected_output": "8"
      }
    ]
  },
  "output": {
    "status": "success",
    "execution_time_ms": 234.5,
    "results": [
      {
        "input": "5 3",
        "expected_output": "8",
        "actual_output": "8",
        "passed": true,
        "error": null
      }
    ],
    "stdout": "",
    "stderr": ""
  }
}
```

### Supported Languages for Execution

| Language | Docker Image | Compiler/Interpreter | Status |
|----------|--------------|-----------------|--------|
| Python | `python:3.11-slim` | Python 3.11 | ✅ Supported |
| C | `gcc:latest` | GCC | ✅ Supported |
| C++ | `gcc:latest` | G++ | ✅ Supported |
| Java | `openjdk:17-slim` | OpenJDK 17 | ✅ Supported |

### Frontend Components

**Available Components:**
- Code editor
- Analysis results panel
- Metrics visualization
- Quality gauges
- Optimization comparison view
- **Test Case Input Panel** (NEW)
- **Execution Output Display** (NEW)
- **Pass/Fail Status Indicators** (NEW)

### Security Guarantees

#### Execution Safety

1. **No Direct Execution**: Code never runs on host machine
2. **Container Isolation**: Each execution gets its own container
3. **Resource Limits**: CPU capped at 0.5 cores, memory at 128MB
4. **Timeout Protection**: Execution fails safely after 5 seconds
5. **Automatic Cleanup**: Containers deleted immediately after execution
6. **Read-Only Filesystem**: Cannot modify system or application files
7. **No Network Access**: Containers cannot make network requests
8. **No Privilege Escalation**: Runs as non-root user

#### Input Validation

- Code size limits enforced
- Language validation required
- Test case format validation
- Input/output string length limits

### Docker Requirements

To use the execution service, ensure:

1. **Docker is installed and running**
   ```bash
   docker --version
   docker run hello-world
   ```

2. **Docker daemon is accessible**
   - Linux: Docker socket at `/var/run/docker.sock`
   - macOS: Docker Desktop running
   - Windows: Docker Desktop with WSL 2

3. **Required images available** (auto-pulled on first use)
   - `python:3.11-slim`
   - `gcc:latest`
   - `openjdk:17-slim`

### Testing the Execution

To verify secure execution works:

**Python Test**
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(int(input()) + 10)",
    "language": "python",
    "test_cases": [
      {"input": "5", "expected_output": "15"}
    ]
  }'
```

**C Test**
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "#include <stdio.h>\nint main() {\n  int x;\n  scanf(\"%d\", &x);\n  printf(\"%d\", x + 10);\n  return 0;\n}",
    "language": "c",
    "test_cases": [
      {"input": "5", "expected_output": "15"}
    ]
  }'
```

### Error Handling

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Docker daemon not running` | Docker service not started | Start Docker service |
| `Execution failed: timeout` | Code takes > 5 seconds | Optimize code for performance |
| `Memory limit exceeded` | Code uses > 128MB RAM | Reduce memory usage |
| `Compilation error` | Invalid C/C++ code | Fix syntax errors |
| `Container not found` | Docker image unavailable | Docker will auto-pull on next try |

### Performance Considerations

- **First execution**: Slower due to Docker image pull/start (~3-5s)
- **Subsequent executions**: Faster as images are cached (~500-2000ms)
- **Memory overhead**: ~50MB per container startup
- **Network**: Not applicable (no network access)

### Compliance & Audit

**Security Checklist:**
- ✅ No code execution on host
- ✅ No subprocess or eval operations
- ✅ Docker container isolation enforced
- ✅ Resource limits configured
- ✅ Network access disabled
- ✅ Filesystem read-only
- ✅ Auto-cleanup of containers
- ✅ Timeout protection
- ✅ Input validation

### Future Security Enhancements

1. **Container Registry**: Use private registries for custom images
2. **Audit Logging**: Log all execution attempts and results
3. **Rate Limiting**: Prevent execution spam/DOS
4. **Execution History**: Track and monitor execution patterns
5. **User Quotas**: Limit execution count per user
6. **Network Monitoring**: Alert on attempted network access
7. **Code Analysis**: Pre-execute static analysis for dangerous patterns
8. **Sandboxing**: Additional seccomp profiles for containers

---

**Last Updated:** February 22, 2026
**Version:** 2.0 - Secure Execution Enabled
**Status:** Docker Sandbox Execution ENABLED

