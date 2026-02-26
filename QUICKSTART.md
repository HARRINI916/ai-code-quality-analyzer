# Quick Setup & Testing Guide

## Prerequisites

Make sure you have installed:
- Python 3.9+ (`python --version`)
- Node.js 16+ (`node --version`)
- Docker (for code execution) - `docker --version`

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Frontend Setup

**In a new terminal:**

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if first time)
npm install

# Start frontend
npm run dev
```

**Expected Output:**
```
VITE v... ready in ... ms
➜  Local:   http://localhost:5173/
```

### 3. Open Browser

Navigate to: **http://localhost:5173**

You should see the AI Code Quality Analyzer dashboard.

## Testing Analysis

### Test 1: Basic Analysis

1. **Verify Language**: Python should be selected
2. **Code Editor**: The starter code should be visible
3. **Click "Analyze"** button
4. **Check Results**:
   - Should show "Complexity: O(n)"
   - Should show metrics (LOC, functions, loops, etc.)
   - Should show quality scores

### Test 2: Code Optimization

1. **After Analysis**: Click **"Optimize Code"** button
2. **Check Results**:
   - Should show optimized code
   - Should show complexity improvement (if applicable)
   - Should enter Compare Mode

### Test 3: Test Cases & Execution

1. **With Code Selected**: Navigate to **"Test Cases"** panel
2. **Add Test Case**:
   - Input: `5`
   - Expected Output: `15`
   - Click **"Add Test Case"**
3. **Expand Test Case**: Click on "Test Case 1"
4. **Fill In**:
   - Input: `5`
   - Expected Output: `15`
5. **Click "Run Tests"**
6. **Check Results**:
   - Should show "PASSED" or "FAILED" status
   - Should show execution time
   - Should show actual output

## API Testing (Optional)

### Test Health

```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy"}
```

### Test Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def f(n): return n * 2",
    "language": "python"
  }'
```

**Expected:** JSON with complexity, metrics, scores, suggestions

### Test Execution

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(int(input()) * 2)",
    "language": "python",
    "test_cases": [{"input": "5", "expected_output": "10"}]
  }'
```

**Expected:** JSON with test results, execution time, pass/fail status

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version

# Check port 8000 is available
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# If port in use, kill process:
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Frontend won't start

```bash
# Clean install
rm -rf node_modules
npm install
npm run dev
```

### Can't analyze code

1. Check backend terminal for errors
2. Open browser DevTools (F12)
3. Check Console tab for error messages
4. Check Network tab to see API requests/responses

### Test execution fails with Docker error

```bash
# Check Docker is running
docker ps

# If not running, start Docker
# macOS/Windows: Open Docker Desktop
# Linux: sudo service docker start

# Or pull required images manually
docker pull python:3.11-slim
```

### CORS errors in browser console

This usually means frontend and backend can't communicate.

**Check:**
1. Both frontend (port 5173) and backend (port 8000) are running
2. Backend has correct CORS_ORIGINS set

## Common File Locations

| Component | Location |
|-----------|----------|
| Backend Main | `backend/app/main.py` |
| API Routes | `backend/app/api/routes.py` |
| Analyzer Service | `backend/app/services/analyzer.py` |
| Sandbox Executor | `backend/app/services/sandbox_executor.py` |
| Frontend App | `frontend/src/App.jsx` |
| Dashboard | `frontend/src/pages/Dashboard.jsx` |
| API Client | `frontend/src/services/api.js` |
| Test Panel | `frontend/src/components/TestCasePanel.jsx` |
| Output Panel | `frontend/src/components/ExecuteOutputPanel.jsx` |

## Feature Support by Language

| Feature | Python | JavaScript | Java | C | C++ | Go |
|---------|--------|-----------|------|---|-----|-----|
| Analysis | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Optimization | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Execution | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |

## Environment Variables

### Backend (.env file in backend/)

```env
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Frontend (.env file in frontend/)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Production Deployment

Not covered in this guide. For production:
1. Use proper environment management
2. Set up proper CORS headers
3. Use production web servers (Gunicorn, Nginx)
4. Enable HTTPS
5. Set up database migrations
6. Use Docker containerization

---

**Issues?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging steps.
