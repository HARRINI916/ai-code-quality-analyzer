import React from "react";

export default function ExecuteOutputPanel({ executionResult, loading }) {
  if (!executionResult && !loading) {
    return null;
  }

  return (
    <div className="card mt-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Execution Results</h3>
        {executionResult?.execution_time_ms && (
          <p className="text-sm text-muted">
            Execution Time: {executionResult.execution_time_ms.toFixed(2)}ms
          </p>
        )}
      </div>

      {loading ? (
        <div className="flex-center py-8">
          <div className="animate-spin text-2xl">⚙️</div>
          <span className="ml-3">Running tests...</span>
        </div>
      ) : executionResult?.status === "error" ? (
        <div className="bg-red-50 dark-mode:bg-red-900/20 border border-red-200 dark-mode:border-red-800 rounded p-4">
          <p className="font-semibold text-red-800 dark-mode:text-red-300 mb-2">
            Execution Error
          </p>
          <pre className="text-sm text-red-700 dark-mode:text-red-400 overflow-auto">
            {executionResult.error || executionResult.stderr}
          </pre>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Test Results */}
          {executionResult?.results && executionResult.results.length > 0 ? (
            <div>
              <h4 className="font-medium mb-3">Test Case Results</h4>
              <div className="space-y-2">
                {executionResult.results.map((result, index) => (
                  <div
                    key={index}
                    className={`border-l-4 p-3 rounded ${
                      result.passed
                        ? "border-green-500 bg-green-50 dark-mode:bg-green-900/10 dark-mode:border-green-600"
                        : "border-red-500 bg-red-50 dark-mode:bg-red-900/10 dark-mode:border-red-600"
                    }`}
                  >
                    <div className="flex-between mb-2">
                      <span className="font-medium text-sm">
                        Test {index + 1}
                      </span>
                      <span
                        className={`badge ${
                          result.passed ? "badge-success" : "badge-error"
                        }`}
                      >
                        {result.passed ? "PASSED" : "FAILED"}
                      </span>
                    </div>

                    {result.error ? (
                      <div className="text-sm text-red-700 dark-mode:text-red-400">
                        <p className="font-medium mb-1">Error:</p>
                        <pre className="overflow-auto text-xs">
                          {result.error}
                        </pre>
                      </div>
                    ) : (
                      <div className="grid grid-2 gap-3 text-sm">
                        <div>
                          <p className="font-medium text-xs text-muted mb-1">
                            Input
                          </p>
                          <pre className="bg-white dark-mode:bg-slate-900 p-2 rounded text-xs overflow-auto max-h-24">
                            {result.input || "(empty)"}
                          </pre>
                        </div>
                        <div>
                          <p className="font-medium text-xs text-muted mb-1">
                            Expected Output
                          </p>
                          <pre className="bg-white dark-mode:bg-slate-900 p-2 rounded text-xs overflow-auto max-h-24">
                            {result.expected_output}
                          </pre>
                        </div>
                        <div>
                          <p className="font-medium text-xs text-muted mb-1">
                            Actual Output
                          </p>
                          <pre className="bg-white dark-mode:bg-slate-900 p-2 rounded text-xs overflow-auto max-h-24">
                            {result.actual_output}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {/* Summary */}
          {executionResult?.results && executionResult.results.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              {(() => {
                const passed = executionResult.results.filter(
                  (r) => r.passed
                ).length;
                const total = executionResult.results.length;
                const percentage = Math.round((passed / total) * 100);

                return (
                  <div className="flex-between">
                    <div>
                      <p className="text-sm font-medium">
                        {passed}/{total} tests passed
                      </p>
                      <p className="text-xs text-muted">{percentage}% success</p>
                    </div>
                    <div
                      className={`text-2xl ${
                        passed === total ? "text-green-600" : "text-orange-600"
                      }`}
                    >
                      {passed === total ? "✓" : `${percentage}%`}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Console Output */}
          {executionResult?.stdout && (
            <div className="mt-4 pt-4 border-t">
              <p className="font-medium text-sm mb-2">Standard Output</p>
              <pre className="bg-slate-900 text-slate-100 p-3 rounded text-xs overflow-auto max-h-32">
                {executionResult.stdout}
              </pre>
            </div>
          )}

          {executionResult?.stderr && (
            <div className="mt-3">
              <p className="font-medium text-sm mb-2 text-red-600">
                Standard Error
              </p>
              <pre className="bg-red-950 text-red-200 p-3 rounded text-xs overflow-auto max-h-32">
                {executionResult.stderr}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
