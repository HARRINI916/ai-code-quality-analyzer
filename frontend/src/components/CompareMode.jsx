import React from "react";
import CodeEditor from "./CodeEditor";

function complexityRank(value) {
  const order = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"];
  const idx = order.indexOf(value);
  return idx === -1 ? order.length : idx;
}

export default function CompareMode({
  language,
  originalCode,
  optimizedCode,
  onLanguageChange,
  onOriginalChange,
  onOptimizedChange,
  onAnalyzeCompare,
  showAnalyzeCompare = true,
  readOnly = false,
  loading,
  complexityImproved = false,
  optimizationType = "",
  originalResult,
  optimizedResult,
  originalErrorMarker,
  optimizedErrorMarker,
}) {
  const canShowSummary = originalResult?.status === "success" && optimizedResult?.status === "success";

  let winner = "Tie";
  let scoreDiff = 0;
  let scorePct = 0;

  if (canShowSummary) {
    scoreDiff = Math.round((optimizedResult.scores.overall || 0) - (originalResult.scores.overall || 0));
    scorePct =
      (originalResult.scores.overall || 0) > 0
        ? Math.round((scoreDiff / originalResult.scores.overall) * 100)
        : 0;
    const originalRank = complexityRank(originalResult.complexity);
    const optimizedRank = complexityRank(optimizedResult.complexity);

    if (scoreDiff > 0 || optimizedRank < originalRank) {
      winner = "Optimized version";
    } else if (scoreDiff < 0 || optimizedRank > originalRank) {
      winner = "Original version";
    }

  }

  const complexityBadgeClass = complexityImproved
    ? "border-emerald-500/60 bg-emerald-500/15 text-emerald-200"
    : "border-slate-500/60 bg-slate-700/40 text-slate-200";

  return (
    <section className="space-y-5">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CodeEditor
          title="Original Code"
          code={originalCode}
          language={language}
          onChange={onOriginalChange}
          onLanguageChange={onLanguageChange}
          loading={loading}
          errorMarker={originalErrorMarker}
          showAnalyzeButton={false}
          showLanguageSelect={!readOnly}
          readOnly={readOnly}
        />
        <CodeEditor
          title="Optimized Code"
          code={optimizedCode}
          language={language}
          onChange={onOptimizedChange}
          onLanguageChange={onLanguageChange}
          loading={loading}
          errorMarker={optimizedErrorMarker}
          showAnalyzeButton={false}
          showLanguageSelect={!readOnly}
          readOnly={readOnly}
        />
      </div>

      {showAnalyzeCompare && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onAnalyzeCompare}
            disabled={loading}
            className="rounded-lg bg-cyan-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Analyzing Compare..." : "Analyze Comparison"}
          </button>
        </div>
      )}

      {canShowSummary && (
        <div className="rounded-3xl border border-slate-700/60 bg-slate-900/70 p-5 shadow-xl shadow-slate-950/35">
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Comparison Summary</h3>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-700 bg-slate-800/70 p-3">
              <p className="text-xs text-slate-400">Original</p>
              <p className="mt-1 text-slate-100">{originalResult.complexity}</p>
              <p className="text-lg font-semibold text-slate-100">{Math.round(originalResult.scores.overall)}</p>
            </div>
            <div className="rounded-2xl border border-emerald-600/60 bg-emerald-500/10 p-3">
              <p className="text-xs text-slate-400">Optimized</p>
              <p className="mt-1 font-semibold text-emerald-300">{optimizedResult.complexity}</p>
              <p className="text-lg font-semibold text-emerald-200">{Math.round(optimizedResult.scores.overall)}</p>
            </div>
            <div className="rounded-2xl border border-cyan-600/70 bg-cyan-500/10 p-3">
              <p className="text-xs text-cyan-200">Improvement</p>
              <p className={`mt-1 text-sm ${complexityImproved ? "text-emerald-200" : "text-cyan-100"}`}>
                {`${originalResult.complexity} -> ${optimizedResult.complexity}`}
              </p>
              <p className="mt-1 text-lg font-semibold text-cyan-100">{scorePct >= 0 ? `+${scorePct}%` : `${scorePct}%`}</p>
              <p className="text-xs text-cyan-200">Better: {winner}</p>
              <p className={`mt-2 inline-block rounded-full border px-2 py-0.5 text-[11px] font-semibold ${complexityBadgeClass}`}>
                {complexityImproved ? "Complexity Improved" : "Complexity Unchanged"}
              </p>
              {optimizationType && (
                <p className="mt-1 inline-block rounded-full border border-emerald-500/60 bg-emerald-500/15 px-2 py-0.5 text-[11px] font-semibold text-emerald-200">
                  {optimizationType === "algorithmic improvement" ? "Algorithm Improved" : optimizationType}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
