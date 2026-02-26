# Troubleshooting Guide - Can't Analyze or Run Code

## Quick Diagnosis

### 1. Check Backend is Running

**In Python Terminal:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

If this fails, the backend isn't running.

### 2. Test Analysis Directly

**Via cURL:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"hello\")",
    "language": "python"
  }'
```

**Expected response:**
```json
{
  "status": "success",
  "complexity": "O(1)",
  "metrics": {...},
  "scores": {...},
  "suggestions": [...]
}
```

### 3. Check Browser Console

**Firefox/Chrome DevTools:**
1. Press `F12` to open DevTools
2. Go to **Console** tab
3. Look for any error messages
4. Check **Network** tab to see API requests

### 4. Check Backend Logs

**In Python Terminal:**
```
Look for any error messages like:
- ImportError: No module named 'analyzer'
- ConnectionError: Failed to connect
- TypeError: unexpected keyword argument
```

## Common Issues & Solutions

### Issue: GET http://localhost:8000/health returns 404

**Cause:** Backend not running

**Solution:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait for: `Application startup complete`

### Issue: POST /analyze returns 500 error

**Cause:** Analyzer module not found or error in analysis

**Solution:**
```bash
# Check analyzer exists
ls backend/app/services/analyzer.py

# Manually test in Python
cd backend
python -c "from app.services.analyzer import CodeAnalyzer; a = CodeAnalyzer(); print('OK')"
```

### Issue: Cannot connect to Docker daemon

**Cause:** Docker not installed or not running

**Solution:**
```bash
# Check docker
docker --version

# If not installed, download from https://docker.com

# Start Docker daemon
docker daemon &

# Verify connection
docker ps
```

**Windows + Docker Desktop "WSL needs updating":**
```bash
wsl --update
wsl --shutdown
```
Then restart Docker Desktop and run `docker ps` again.

### Issue: Test cases don't run but analysis works

**Cause:** Docker not available or execution service issue

**Solution:**
```bash
# Check test cases format in request
# Verify language is supported: python, c, cpp, java

# Test Docker directly
docker run hello-world

# If above works, try:
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"hello\")",
    "language": "python",
    "test_cases": [{"input": "", "expected_output": "hello"}]
  }'
```

### Issue: Frontend can't reach backend

**Cause:** CORS issue or wrong API URL

**Solution:**
1. Open DevTools → Network tab
2. Try to trigger analyze/optimize
3. Check if request is made
4. Check response headers for CORS errors

If CORS error:
```bash
# Check backend CORS_ORIGINS environment variable
env | grep CORS

# Should include: http://localhost:5173 (frontend URL)
```

### Issue: Code runs but shows as failed test

**Cause:** Output format mismatch (extra newlines, spaces, etc)

**Solution:**
```
Expected: "15"
Actual: "15\n"

Remove trailing newline in expected output!
```

## Step-by-Step Debug

### 1. Start Fresh

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Wait for "Application startup complete"
```

```bash
# Terminal 2: Frontend
cd frontend
npm run dev

# Should see: "VITE v... ready in ... ms"
```

### 2. Test Backend Health

```bash
# Terminal 3: Testing
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 3. Test Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def f(n): return n",
    "language": "python"
  }' | jq '.'
```

### 4. Test Execution (if Docker running)

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(42)",
    "language": "python",
    "test_cases": [{"input": "", "expected_output": "42"}]
  }' | jq '.'
```

### 5. Open Frontend

```
http://localhost:5173
```

1. Select Python language
2. Paste code: `def f(x): return x * 2`
3. Click "Analyze"
4. Check browser console for errors

## Backend Error Messages

### ImportError: No module named X

```
Solution: pip install -r requirements.txt
```

### AttributeError: 'X' object has no attribute 'Y'

```
Solution: 
- Check file syntax
- Restart backend (Ctrl+C, then python -m ...)
```

### ConnectionError: Failed to connect to Docker daemon

```
Solution:
- Docker is optional for basic analysis
- Only needed for /execute endpoint
- If Docker not available, /analyze and /optimize still work
```

### ValueError: Unsupported language

```
Solution: 
- Use: python, c, cpp, java (for execution)
- Use: python, javascript, java, cpp, c, go (for analysis)
```

## Logs to Check

### Backend startup:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API response:
Open browser Network tab, look at Response/Preview tabs

### Frontend requests:
DevTools → Network → click on request → Response tab

## If All Else Fails

### Reset and Restart

```bash
# Kill all processes
Ctrl+C  (in all terminals)

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Restart
# (Follow step-by-step debug above)
```

### Check File Permissions

```bash
# Ensure files are readable
chmod +x backend/app/main.py
```

---

Still having issues? Check:
1. Python version: `python --version` (should be 3.9+)
2. Node version: `node --version` (should be 16+)  
3. All terminals show no errors in startup
4. Firewall not blocking localhost:8000 or localhost:5173
