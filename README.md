**CODEPULSE AI**

Project Overview

AI Code Quality and Complexity Analyzer is a web-based application that analyzes source code and provides insights about its quality, structure, and performance.
The system performs static code analysis, calculates exact time complexity in Big-O notation, detects potential issues, runs test cases in a secure sandbox, and generates optimized versions of the code when possible.
This project is designed to help students and developers understand code performance and improve algorithm efficiency.

**Features**

Analyze code and compute exact time complexity (O(1), O(n), O(n²), etc.)

Detect nested loops and recursion patterns

Provide detailed code metrics:

Lines of Code

Number of Functions

Number of Loops

Nesting Depth

Cyclomatic Complexity

Show quality score breakdown:

Readability

Maintainability

Efficiency

Safety

Detect extra issues such as:

Function defined but not called

Missing print/output statement

Run test cases in a secure sandbox environment

Compare expected and actual output

Automatically optimize inefficient code

Show side-by-side comparison of original and optimized code

Display complexity improvement (example: O(n³) → O(n²))

**Tech Stack**

Frontend

React (Vite)

Tailwind CSS

Monaco Editor

Backend

FastAPI (Python)

AST-based static analysis

Secure sandbox execution

Tools and Concepts

Big-O complexity detection

Code optimization logic

Docker-based isolated execution (if enabled)

Structural output comparison

**Project Structure**

ai-code-quality-analyzer/

    │
    ├── frontend/               # React frontend
    │   ├── src/
    │   ├── components/
    │   └── pages/
    │
    ├── backend/                # FastAPI backend
    │   ├── app/
    │   │   ├── routes/
    │   │   ├── services/
    │   │   └── models/
    │   └── requirements.txt
    │
    ├── README.md
    └── .gitignore
    
**Application Workflow**

Page 1 – Code Editor
User writes or pastes code

Click Analyze to go to analysis page

Click Optimize to directly generate optimized version

Page 2 – Analysis and Test Cases

Shows:

Exact Big-O complexity

Code metrics

Score breakdown

User can add test cases

Run test cases and see:

Actual output

Expected output

Pass or Fail

Execution time

Page 3 – Optimization and Comparison

Displays original code

Displays optimized code

Shows complexity comparison

Shows score improvement

**Running the Project Locally**

1.Clone the repository
   
    git clone https://github.com/yourusername/ai-code-quality-analyzer.git
    cd ai-code-quality-analyzer
   
2.Setup Backend

    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload
      
3.Backend runs at:

    http://localhost:8000
      
4.Setup Frontend
Open a new terminal:

    cd frontend
    npm install
    npm run dev
5.Frontend runs at:
      
    http://localhost:5173
    
**Author**

Harrini D S

GitHub: https://github.com/HARRINI916

