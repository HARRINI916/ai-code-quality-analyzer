import React from "react";

export default function TestCasePanel({ testCases, onTestCasesChange, onRunTests, loading, disabled = false }) {
  function addTestCase() {
    onTestCasesChange([...testCases, { input: "", expected_output: "" }]);
  }

  function removeTestCase(index) {
    onTestCasesChange(testCases.filter((_, i) => i !== index));
  }

  function updateCase(index, field, value) {
    const next = [...testCases];
    next[index] = { ...next[index], [field]: value };
    onTestCasesChange(next);
  }

  return (
    <section className="saas-card test-case-panel">
      <div className="panel-head">
        <h3>Test Cases</h3>
        <button type="button" onClick={addTestCase} disabled={disabled} className="btn-secondary">
          Add Test Case
        </button>
      </div>

      <div className="stack-md">
        {testCases.map((item, index) => (
          <article key={index} className="test-case-item">
            <div className="panel-head">
              <h4>Case {index + 1}</h4>
              <button type="button" onClick={() => removeTestCase(index)} className="btn-link">
                Remove
              </button>
            </div>
            <div className="test-grid">
              <label>
                Input
                <textarea
                  value={item.input}
                  onChange={(event) => updateCase(index, "input", event.target.value)}
                  rows={3}
                  placeholder="Optional input"
                />
              </label>
              <label>
                Expected Output
                <textarea
                  value={item.expected_output}
                  onChange={(event) => updateCase(index, "expected_output", event.target.value)}
                  rows={3}
                  placeholder="Expected output"
                />
              </label>
            </div>
          </article>
        ))}
      </div>

      {testCases.length === 0 && <p className="empty-text">No test cases added yet.</p>}

      <div className="actions-end">
        <button
          type="button"
          onClick={() => onRunTests(testCases)}
          disabled={disabled || loading || testCases.length === 0}
          className="btn-primary"
        >
          {loading ? "Running Tests..." : "Run Tests"}
        </button>
      </div>
    </section>
  );
}
