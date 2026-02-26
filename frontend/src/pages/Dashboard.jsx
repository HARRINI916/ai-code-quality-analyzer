import React, { useMemo, useState } from "react";
import CodeEditor from "../components/CodeEditor";
import MetricsPanel from "../components/MetricsPanel";
import ScoreBreakdown from "../components/ScoreBreakdown";
import SuggestionsPanel from "../components/SuggestionsPanel";
import ExtraIssuesPanel from "../components/ExtraIssuesPanel";
import CompareMode from "../components/CompareMode";
import TestCasePanel from "../components/TestCasePanel";
import OutputPanel from "../components/OutputPanel";
import OptimizePanel from "../components/OptimizePanel";
import { analyze, optimize, execute, formatApiError } from "../services/api";

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

export default function Dashboard() {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(starterByLanguage.python);
  const [loading, setLoading] = useState(false);
  const [testRunning, setTestRunning] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState("");

  const [analysisResult, setAnalysisResult] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [executionResult, setExecutionResult] = useState(null);

  const [optimizedCode, setOptimizedCode] = useState(null);
  const [optimizationNote, setOptimizationNote] = useState("");
  const [optimizationType, setOptimizationType] = useState("");
  const [complexityImproved, setComplexityImproved] = useState(false);
  const [optimizedComplexity, setOptimizedComplexity] = useState("");
  const [originalComplexity, setOriginalComplexity] = useState("");
  const [originalScore, setOriginalScore] = useState(0);
  const [optimizedScore, setOptimizedScore] = useState(0);

  const [compareEnabled, setCompareEnabled] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [originalResult, setOriginalResult] = useState(null);
  const [optimizedResult, setOptimizedResult] = useState(null);

  const shellClass = useMemo(
    () => "min-h-screen bg-[radial-gradient(circle_at_top,_#172554_0%,_#0f172a_45%,_#020617_100%)] text-slate-100",
    [],
  );

  async function handleAnalyze() {
    setLoading(true);
    setError("");
    try {
      const data = await analyze(code, language);
      if (data?.status === "error") {
        setAnalysisResult(null);
        setError(`${data.error_type?.toUpperCase() || "ERROR"} error at line ${data.line || "?"}: ${data.message || "Unknown error"}`);
        return;
      }
      setAnalysisResult(data);
      setOriginalComplexity(data.complexity);
      setOriginalScore(data.scores?.overall || 0);
      setExecutionResult(null);
      setOptimizedCode(null);
      setCompareEnabled(false);
      setOriginalResult(null);
      setOptimizedResult(null);
    } catch (err) {
      setError(formatApiError(err, "Failed to analyze code"));
    } finally {
      setLoading(false);
    }
  }

  async function handleRunTests() {
    setTestRunning(true);
    setError("");
    try {
      const result = await execute(code, language, testCases);
      setExecutionResult(result);
    } catch (err) {
      setExecutionResult({
        status: "error",
        error: formatApiError(err, "Failed to execute code"),
        execution_time_ms: 0,
        results: [],
        stdout: "",
        stderr: "",
      });
    } finally {
      setTestRunning(false);
    }
  }

  async function handleOptimize() {
    if (!analysisResult || analysisResult.status !== "success") {
      return;
    }
    setOptimizing(true);
    setError("");
    try {
      const data = await optimize(code, language);
      if (data?.status === "error") {
        setError(`${data.error_type?.toUpperCase() || "ERROR"} error at line ${data.line || "?"}: ${data.message || "Unknown error"}`);
        return;
      }

      setOptimizedCode(data.optimized_code);
      setOptimizationNote(data.notes || "");
      setOptimizationType(data.optimization_type || "");
      setComplexityImproved(Boolean(data.complexity_improved));
      setOptimizedComplexity(data.optimized_complexity || "");
      setOriginalComplexity(data.original_complexity || analysisResult.complexity);
      setOriginalScore(data.original_score || analysisResult.scores?.overall || 0);
      setOptimizedScore(data.optimized_score || 0);
      setCompareEnabled(true);
    } catch (err) {
      setError(formatApiError(err, "Failed to optimize code"));
    } finally {
      setOptimizing(false);
    }
  }

  async function handleAnalyzeCompare() {
    if (!optimizedCode) return;
    setCompareLoading(true);
    setError("");
    try {
      const [original, optimized] = await Promise.all([analyze(code, language), analyze(optimizedCode, language)]);
      setOriginalResult(original?.status === "success" ? original : null);
      setOptimizedResult(optimized?.status === "success" ? optimized : null);
      if (original?.status === "error") {
        setError(`Original code: ${original.message}`);
      }
      if (optimized?.status === "error") {
        setError((prev) => (prev ? `${prev} | Optimized code: ${optimized.message}` : `Optimized code: ${optimized.message}`));
      }
    } catch (err) {
      setError(formatApiError(err, "Failed to analyze compare mode"));
    } finally {
      setCompareLoading(false);
    }
  }

  function handleLanguageChange(nextLanguage) {
    const starter = starterByLanguage[nextLanguage] || "";
    setLanguage(nextLanguage);
    setCode(starter);
    setError("");
    setAnalysisResult(null);
    setExecutionResult(null);
    setTestCases([]);
    setOptimizedCode(null);
    setOptimizationNote("");
    setOptimizationType("");
    setComplexityImproved(false);
    setOptimizedComplexity("");
    setOriginalComplexity("");
    setOriginalResult(null);
    setOptimizedResult(null);
    setCompareEnabled(false);
  }

  const canRunTests = Boolean(analysisResult?.status === "success");
  const showAnalysis = analysisResult?.status === "success";
  const showOutput = Boolean(executionResult);
  const showOptimizeAndCompare = Boolean(optimizedCode);

  return (
    <main className={shellClass}>
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8">
        <header className="rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/35 backdrop-blur-xl">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">AI Code Quality Analyzer</h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-300">Workflow: Code to Analysis to Test Cases to Output to Optimize to Compare</p>
            </div>
            <div className="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.15em] text-cyan-200">
              Structured Flow
            </div>
          </div>
          {error && <p className="mt-4 rounded-2xl border border-rose-600/50 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</p>}
        </header>

        <CodeEditor
          title="1. Code Editor"
          code={code}
          language={language}
          onChange={setCode}
          onLanguageChange={handleLanguageChange}
          onAnalyze={handleAnalyze}
          onRunTests={handleRunTests}
          loading={loading}
          runLoading={testRunning}
          runDisabled={!canRunTests || language === "javascript" || language === "go"}
          showAnalyzeButton
          showRunTestsButton
        />

        {showAnalysis && (
          <section className="animate-[slideInUp_.35s_ease] space-y-4">
            <div className="rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/35">
              <h2 className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">2. Complexity & Analysis Results</h2>
              <div className="rounded-3xl border border-cyan-500/40 bg-gradient-to-r from-cyan-500/15 to-blue-500/10 p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Exact Big-O</p>
                <p className="mt-1 text-4xl font-bold text-cyan-100">{analysisResult.complexity}</p>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <ScoreBreakdown scores={analysisResult.scores} />
              <MetricsPanel metrics={analysisResult.metrics} />
            </div>
            <ExtraIssuesPanel issues={analysisResult.extra_issues} />
            {analysisResult.suggestions?.length > 0 && <SuggestionsPanel suggestions={analysisResult.suggestions} />}
          </section>
        )}

        {showAnalysis && (
          <section>
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">3. Test Case Section</h2>
            <TestCasePanel
              testCases={testCases}
              onTestCasesChange={setTestCases}
              onRunTests={handleRunTests}
              loading={testRunning}
              disabled={language === "javascript" || language === "go"}
            />
          </section>
        )}

        {showOutput && (
          <section>
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">4. Execution Output Section</h2>
            <OutputPanel executionResult={executionResult} loading={testRunning} />
          </section>
        )}

        {(showOutput || showOptimizeAndCompare) && (
          <section>
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">5. Optimize Mode Section</h2>
            <OptimizePanel
              language={language}
              optimizedCode={optimizedCode}
              optimizationNote={optimizationNote}
              optimizedComplexity={optimizedComplexity}
              originalComplexity={originalComplexity}
              optimizationType={optimizationType}
              complexityImproved={complexityImproved}
              optimizing={optimizing}
              onOptimize={handleOptimize}
            />
          </section>
        )}

        {showOptimizeAndCompare && (
          <section className="animate-[slideInUp_.35s_ease] rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/35">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">6. Compare Mode Section</h2>
              <button
                type="button"
                onClick={() => setCompareEnabled((prev) => !prev)}
                className="rounded-xl border border-cyan-500/50 bg-cyan-500/10 px-4 py-2 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-500/20"
              >
                {compareEnabled ? "Hide Compare Mode" : "Show Compare Mode"}
              </button>
            </div>

            <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-700 bg-slate-800/70 p-3">
                <p className="text-xs text-slate-400">Original Score</p>
                <p className="text-lg font-semibold text-slate-100">{Math.round(originalScore)}</p>
              </div>
              <div className="rounded-2xl border border-emerald-600/50 bg-emerald-500/10 p-3">
                <p className="text-xs text-emerald-200">Optimized Score</p>
                <p className="text-lg font-semibold text-emerald-100">{Math.round(optimizedScore)}</p>
              </div>
              <div className="rounded-2xl border border-cyan-600/50 bg-cyan-500/10 p-3">
                <p className="text-xs text-cyan-200">Score Improvement</p>
                <p className="text-lg font-semibold text-cyan-100">{optimizedScore - originalScore >= 0 ? "+" : ""}{Math.round(optimizedScore - originalScore)}</p>
              </div>
            </div>

            {compareEnabled && (
              <CompareMode
                language={language}
                originalCode={code}
                optimizedCode={optimizedCode}
                onLanguageChange={handleLanguageChange}
                onOriginalChange={setCode}
                onOptimizedChange={setOptimizedCode}
                onAnalyzeCompare={handleAnalyzeCompare}
                showAnalyzeCompare
                readOnly
                loading={compareLoading}
                complexityImproved={complexityImproved}
                optimizationType={optimizationType}
                originalResult={originalResult}
                optimizedResult={optimizedResult}
              />
            )}
          </section>
        )}
      </div>
    </main>
  );
}
