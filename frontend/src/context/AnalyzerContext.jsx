import React, { createContext, useContext, useMemo, useState } from "react";
import { analyze, execute, formatApiError, optimize } from "../services/api";

const starterByLanguage = {
  python: `def process_items(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
    return total
`,
  c: `#include <stdio.h>
int sum_positive(int *arr, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i] > 0) total += arr[i];
    }
    return total;
}
`,
  cpp: `#include <vector>
int sumPositive(const std::vector<int>& nums) {
    int total = 0;
    for (int n : nums) {
        if (n > 0) total += n;
    }
    return total;
}
`,
  java: `public class Main {
    static int sumPositive(int[] nums) {
        int total = 0;
        for (int n : nums) {
            if (n > 0) total += n;
        }
        return total;
    }
}
`,
  javascript: `function sumPositive(nums) {
  let total = 0;
  for (const n of nums) {
    if (n > 0) total += n;
  }
  return total;
}
`,
  go: `package main
func sumPositive(nums []int) int {
    total := 0
    for _, n := range nums {
        if n > 0 {
            total += n
        }
    }
    return total
}
`,
};

const complexityOrder = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"];

function complexityRank(value) {
  const idx = complexityOrder.indexOf(value);
  return idx === -1 ? complexityOrder.length : idx;
}

function executableRegex(language) {
  const byLanguage = {
    python: /(return|print\s*\()/,
    javascript: /(return|console\.log\s*\()/,
    java: /(return|System\.out\.println\s*\()/,
    c: /(return|printf\s*\()/,
    cpp: /(return|printf\s*\()/,
    go: /(return|fmt\.Print)/,
  };
  return byLanguage[language] || /return/;
}

const AnalyzerContext = createContext(null);

export function AnalyzerProvider({ children }) {
  const [language, setLanguage] = useState("python");
  const [originalCode, setOriginalCode] = useState(starterByLanguage.python);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [executionResults, setExecutionResults] = useState(null);
  const [optimizedCode, setOptimizedCode] = useState("");
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState({ analyze: false, execute: false, optimize: false });
  const [error, setError] = useState("");

  function setLanguageAndReset(nextLanguage) {
    setLanguage(nextLanguage);
    setOriginalCode(starterByLanguage[nextLanguage] || "");
    setAnalysisResult(null);
    setTestCases([]);
    setExecutionResults(null);
    setOptimizedCode("");
    setComparisonData(null);
    setError("");
  }

  async function runAnalyze() {
    setLoading((prev) => ({ ...prev, analyze: true }));
    setError("");
    try {
      const data = await analyze(originalCode, language);
      if (data?.status === "error") {
        const message = `${data.error_type?.toUpperCase() || "ERROR"} at line ${data.line || "?"}: ${data.message || "Unknown error"}`;
        setError(message);
        setAnalysisResult(null);
        return { ok: false, error: message };
      }
      setAnalysisResult(data);
      return { ok: true, data };
    } catch (err) {
      const message = formatApiError(err, "Failed to analyze code");
      setError(message);
      setAnalysisResult(null);
      return { ok: false, error: message };
    } finally {
      setLoading((prev) => ({ ...prev, analyze: false }));
    }
  }

  async function runExecute() {
    setLoading((prev) => ({ ...prev, execute: true }));
    setError("");
    try {
      const result = await execute(originalCode, language, testCases);
      setExecutionResults(result);
      return { ok: true, data: result };
    } catch (err) {
      const message = formatApiError(err, "Failed to execute code");
      const payload = { status: "error", error: message, execution_time_ms: 0, results: [] };
      setExecutionResults(payload);
      setError(message);
      return { ok: false, error: message };
    } finally {
      setLoading((prev) => ({ ...prev, execute: false }));
    }
  }

  function validateOptimization(optimizedPayload) {
    const originalComplexity = optimizedPayload.original_complexity || analysisResult?.complexity || "";
    const nextComplexity = optimizedPayload.optimized_complexity || "";
    const originalScore = optimizedPayload.original_score ?? analysisResult?.scores?.overall ?? 0;
    const nextScore = optimizedPayload.optimized_score ?? 0;

    const messages = [];
    if (!optimizedPayload.optimized_code?.trim()) {
      messages.push("Optimized code is empty.");
    }
    if (complexityRank(nextComplexity) >= complexityRank(originalComplexity)) {
      messages.push("Optimized complexity is not lower than original complexity.");
    }
    if (!executableRegex(language).test(optimizedPayload.optimized_code || "")) {
      messages.push("Optimized code may be missing a return/print statement.");
    }

    return {
      originalComplexity,
      optimizedComplexity: nextComplexity,
      originalScore,
      optimizedScore: nextScore,
      scoreImprovement: Math.round(nextScore - originalScore),
      complexityImproved: complexityRank(nextComplexity) < complexityRank(originalComplexity),
      isValid: messages.length === 0,
      messages,
      optimizationType: optimizedPayload.optimization_type || "",
      notes: optimizedPayload.notes || "",
    };
  }

  async function runOptimize() {
    setLoading((prev) => ({ ...prev, optimize: true }));
    setError("");
    try {
      if (!analysisResult?.complexity) {
        const analyzeResult = await runAnalyze();
        if (!analyzeResult.ok) {
          return analyzeResult;
        }
      }
      const data = await optimize(originalCode, language);
      if (data?.status === "error") {
        const message = `${data.error_type?.toUpperCase() || "ERROR"} at line ${data.line || "?"}: ${data.message || "Unknown error"}`;
        setError(message);
        return { ok: false, error: message };
      }
      setOptimizedCode(data.optimized_code || "");
      const comparison = validateOptimization(data);
      setComparisonData(comparison);
      return { ok: true, data, comparison };
    } catch (err) {
      const message = formatApiError(err, "Failed to optimize code");
      setError(message);
      return { ok: false, error: message };
    } finally {
      setLoading((prev) => ({ ...prev, optimize: false }));
    }
  }

  const value = useMemo(
    () => ({
      language,
      originalCode,
      analysisResult,
      testCases,
      executionResults,
      optimizedCode,
      comparisonData,
      loading,
      error,
      setError,
      setOriginalCode,
      setTestCases,
      setLanguageAndReset,
      runAnalyze,
      runExecute,
      runOptimize,
    }),
    [language, originalCode, analysisResult, testCases, executionResults, optimizedCode, comparisonData, loading, error],
  );

  return <AnalyzerContext.Provider value={value}>{children}</AnalyzerContext.Provider>;
}

export function useAnalyzer() {
  const context = useContext(AnalyzerContext);
  if (!context) {
    throw new Error("useAnalyzer must be used within AnalyzerProvider");
  }
  return context;
}
