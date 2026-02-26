import React from "react";

export default function OutputPanel({ executionResult, loading }) {
  if (!executionResult && !loading) {
    return null;
  }

  const rows = executionResult?.results || [];
  const passed = rows.filter((row) => row.passed).length;

  return (
    <section className="saas-card">
      <div className="panel-head">
        <h3>Execution Output</h3>
        {executionResult?.execution_time_ms != null && (
          <span className="pill">Execution: {executionResult.execution_time_ms.toFixed(2)} ms</span>
        )}
      </div>

      {loading && <p>Running tests...</p>}

      {!loading && executionResult?.status === "error" && <div className="error-box">{executionResult.error || "Execution failed"}</div>}

      {!loading && executionResult?.status === "success" && (
        <div className="output-wrap">
          <div className="table-scroll">
            <table className="result-table">
              <thead>
                <tr>
                  <th>Input</th>
                  <th>Expected Output</th>
                  <th>Actual Output</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${index}-${row.input}`}>
                    <td>{row.input || "(empty)"}</td>
                    <td>{row.expected_output}</td>
                    <td>{row.actual_output}</td>
                    <td>
                      <span className={row.passed ? "status-pass" : "status-fail"}>{row.passed ? "Pass" : "Fail"}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="summary-line">
            {passed}/{rows.length} tests passed
          </p>
        </div>
      )}
    </section>
  );
}
