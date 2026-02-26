import React from "react";
import { Link } from "react-router-dom";
import MonacoPanel from "../components/MonacoPanel";
import MetricsPanel from "../components/MetricsPanel";
import OutputPanel from "../components/OutputPanel";
import ScoreBreakdown from "../components/ScoreBreakdown";
import SuggestionsPanel from "../components/SuggestionsPanel";
import TestCasePanel from "../components/TestCasePanel";
import ExtraIssuesPanel from "../components/ExtraIssuesPanel";
import { useAnalyzer } from "../context/AnalyzerContext";

export default function AnalysisPage() {
  const {
    language,
    originalCode,
    analysisResult,
    testCases,
    executionResults,
    loading,
    error,
    setTestCases,
    runExecute,
    runAnalyze,
  } = useAnalyzer();

  return (
    <section className="page stack-lg">
      <div className="saas-card">
        <div className="panel-head">
          <h2>Analysis and Test Cases</h2>
          <button type="button" className="btn-secondary" onClick={runAnalyze} disabled={loading.analyze}>
            {loading.analyze ? "Refreshing..." : "Refresh Analysis"}
          </button>
        </div>
      </div>

      <MonacoPanel title="Original Code (Read Only)" code={originalCode} language={language} readOnly />

      {!analysisResult && (
        <div className="saas-card">
          <p>No analysis result available. Go to the code page and run Analyze.</p>
          <Link to="/" className="btn-primary inline-btn">
            Go to Code Page
          </Link>
        </div>
      )}

      {analysisResult?.status === "success" && (
        <div className="stack-lg">
          <section className="saas-card">
            <h3 className="section-title">Exact Big-O Complexity</h3>
            <p className="complexity-value">{analysisResult.complexity}</p>
          </section>

          <div className="analysis-grid">
            <ScoreBreakdown scores={analysisResult.scores} />
            <MetricsPanel metrics={analysisResult.metrics} />
          </div>
          <ExtraIssuesPanel issues={analysisResult.extra_issues} />
          <SuggestionsPanel suggestions={analysisResult.suggestions} />
        </div>
      )}

      <TestCasePanel
        testCases={testCases}
        onTestCasesChange={setTestCases}
        onRunTests={runExecute}
        loading={loading.execute}
        disabled={!analysisResult || language === "javascript" || language === "go"}
      />

      <OutputPanel executionResult={executionResults} loading={loading.execute} />

      {error && <div className="error-box">{error}</div>}
    </section>
  );
}
