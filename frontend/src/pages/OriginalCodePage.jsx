import React from "react";
import { useNavigate } from "react-router-dom";
import MonacoPanel from "../components/MonacoPanel";
import { useAnalyzer } from "../context/AnalyzerContext";

export default function OriginalCodePage() {
  const navigate = useNavigate();
  const {
    language,
    originalCode,
    loading,
    error,
    setOriginalCode,
    setLanguageAndReset,
    runAnalyze,
    runOptimize,
  } = useAnalyzer();

  async function onAnalyze() {
    const result = await runAnalyze();
    if (result.ok) {
      navigate("/analysis");
    }
  }

  async function onOptimize() {
    const result = await runOptimize();
    if (result.ok) {
      navigate("/optimize");
    }
  }

  return (
    <section className="page stack-lg">
      <div className="saas-card">
        <div className="panel-head">
          <h2>Original Code</h2>
          <select value={language} onChange={(event) => setLanguageAndReset(event.target.value)} className="lang-select">
            <option value="python">Python</option>
            <option value="c">C</option>
            <option value="cpp">C++</option>
            <option value="java">Java</option>
            <option value="javascript">JavaScript</option>
            <option value="go">Go</option>
          </select>
        </div>
        <p className="muted">Write or paste code, then continue to analysis or optimization.</p>
      </div>

      <MonacoPanel title="Code Editor" code={originalCode} language={language} onChange={setOriginalCode} />

      {error && <div className="error-box">{error}</div>}

      <div className="actions-end gap-sm">
        <button type="button" className="btn-secondary" onClick={onAnalyze} disabled={loading.analyze}>
          {loading.analyze ? "Analyzing..." : "Analyze"}
        </button>
        <button type="button" className="btn-primary" onClick={onOptimize} disabled={loading.optimize}>
          {loading.optimize ? "Optimizing..." : "Optimize"}
        </button>
      </div>
    </section>
  );
}
