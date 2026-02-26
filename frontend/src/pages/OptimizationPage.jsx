import React, { useEffect, useRef } from "react";
import MonacoPanel from "../components/MonacoPanel";
import { useAnalyzer } from "../context/AnalyzerContext";

export default function OptimizationPage() {
  const { language, originalCode, optimizedCode, comparisonData, loading, error, runOptimize } = useAnalyzer();
  const autoTriggeredRef = useRef(false);

  useEffect(() => {
    if (!autoTriggeredRef.current && !optimizedCode && !loading.optimize) {
      autoTriggeredRef.current = true;
      runOptimize();
    }
  }, [optimizedCode, loading.optimize, runOptimize]);

  return (
    <section className="page stack-lg">
      <div className="saas-card">
        <div className="panel-head">
          <h2>Optimization</h2>
          <button type="button" className="btn-primary" onClick={runOptimize} disabled={loading.optimize}>
            {loading.optimize ? "Optimizing..." : "Re-run Optimization"}
          </button>
        </div>
      </div>

      <div className="opt-grid">
        <MonacoPanel title="Original Code (Read Only)" code={originalCode} language={language} readOnly />
        <MonacoPanel title="Optimized Code (Read Only)" code={optimizedCode || ""} language={language} readOnly />
      </div>

      {comparisonData && (
        <section className="saas-card stack-md">
          <h3 className="section-title">Optimization Summary</h3>
          <div className="comparison-banner">
            <div>
              <p>Original Complexity</p>
              <strong>{comparisonData.originalComplexity}</strong>
            </div>
            <div>
              <p>Optimized Complexity</p>
              <strong>{comparisonData.optimizedComplexity}</strong>
            </div>
            <div>
              <p>Complexity Shift</p>
              <strong>{comparisonData.originalComplexity} to {comparisonData.optimizedComplexity}</strong>
            </div>
            <div>
              <p>Score Improvement</p>
              <strong>{comparisonData.scoreImprovement >= 0 ? "+" : ""}{comparisonData.scoreImprovement}</strong>
            </div>
          </div>

          <div className="badges">
            <span className={comparisonData.complexityImproved ? "badge-good" : "badge-warn"}>
              {comparisonData.complexityImproved ? "Complexity Improved" : "No Complexity Improvement"}
            </span>
            <span className={comparisonData.isValid ? "badge-good" : "badge-warn"}>
              {comparisonData.isValid ? "Validation Passed" : "Validation Needs Review"}
            </span>
          </div>

          {comparisonData.optimizationType && <p>Optimization Type: {comparisonData.optimizationType}</p>}
          {comparisonData.notes && <p>Summary: {comparisonData.notes}</p>}
          {comparisonData.messages?.length > 0 && (
            <ul className="validation-list">
              {comparisonData.messages.map((message, idx) => (
                <li key={`${idx}-${message}`}>{message}</li>
              ))}
            </ul>
          )}
        </section>
      )}

      {error && <div className="error-box">{error}</div>}
    </section>
  );
}
