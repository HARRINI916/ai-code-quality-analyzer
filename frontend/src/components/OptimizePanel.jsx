import React from "react";
import CodeEditor from "./CodeEditor";

export default function OptimizePanel({
  language,
  optimizedCode,
  optimizationNote,
  optimizedComplexity,
  originalComplexity,
  optimizationType,
  complexityImproved,
  optimizing,
  onOptimize,
}) {
  return (
    <section className="animate-[slideInUp_.35s_ease] rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/35">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Optimize Mode</h3>
          <p className="mt-1 text-sm text-slate-300">Generate improved code and compare complexity impact.</p>
        </div>
        <button
          type="button"
          onClick={onOptimize}
          disabled={optimizing}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {optimizing && <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-r-transparent" />}
          {optimizing ? "Optimizing..." : "Optimize Code"}
        </button>
      </div>

      {optimizedCode && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
            <div className="rounded-2xl border border-cyan-600/50 bg-cyan-500/10 p-3">
              <p className="text-xs uppercase tracking-wide text-cyan-200">Complexity</p>
              <p className="mt-1 text-sm text-cyan-100">{`${originalComplexity || "-"} -> ${optimizedComplexity || "-"}`}</p>
            </div>
            <div className="rounded-2xl border border-emerald-600/50 bg-emerald-500/10 p-3">
              <p className="text-xs uppercase tracking-wide text-emerald-200">Improved</p>
              <p className="mt-1 text-sm text-emerald-100">{complexityImproved ? "Yes" : "No"}</p>
            </div>
            <div className="rounded-2xl border border-slate-600/70 bg-slate-800/60 p-3">
              <p className="text-xs uppercase tracking-wide text-slate-300">Optimization Type</p>
              <p className="mt-1 text-sm text-slate-100">{optimizationType || "N/A"}</p>
            </div>
          </div>

          {optimizationNote && (
            <p className="rounded-2xl border border-cyan-600/40 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-100">
              {optimizationNote}
            </p>
          )}

          <CodeEditor
            title="Optimized Code (Read Only)"
            code={optimizedCode}
            language={language}
            onChange={() => {}}
            onLanguageChange={() => {}}
            showAnalyzeButton={false}
            showRunTestsButton={false}
            showLanguageSelect={false}
            readOnly
          />
        </div>
      )}

      {!optimizedCode && !optimizing && (
        <p className="text-sm text-slate-400">Run optimization to reveal the improved code and summary.</p>
      )}
    </section>
  );
}
