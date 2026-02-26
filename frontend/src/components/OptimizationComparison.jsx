import React, { useMemo, useState } from "react";
import CodeEditor from "./CodeEditor";

function complexityRank(value) {
  const order = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"];
  const idx = order.indexOf(value);
  return idx === -1 ? order.length : idx;
}

export default function OptimizationComparison({
  language,
  originalCode,
  optimizedCode,
  originalComplexity,
  optimizedComplexity,
  originalScore,
  optimizedScore,
  improvements,
}) {
  const [view, setView] = useState("optimized");

  const stats = useMemo(() => {
    const scoreDiff = Math.round((optimizedScore || 0) - (originalScore || 0));
    const pct = originalScore > 0 ? Math.round((scoreDiff / originalScore) * 100) : 0;
    const complexityImproved = complexityRank(optimizedComplexity) < complexityRank(originalComplexity);
    const scoreImproved = scoreDiff > 0;
    return {
      scoreDiff,
      pct,
      complexityImproved,
      scoreImproved,
    };
  }, [optimizedScore, originalScore, optimizedComplexity, originalComplexity]);

  return (
    <section className="space-y-4 rounded-2xl border border-cyan-500/30 bg-cyan-500/5 p-4 shadow-lg shadow-slate-950/20">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-cyan-200">Optimization Result</h3>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
              view === "original" ? "bg-slate-700 text-slate-100" : "bg-slate-800/70 text-slate-300"
            }`}
            onClick={() => setView("original")}
          >
            Original
          </button>
          <button
            type="button"
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${
              view === "optimized" ? "bg-cyan-500 text-slate-950" : "bg-slate-800/70 text-slate-300"
            }`}
            onClick={() => setView("optimized")}
          >
            Optimized
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-3 md:col-span-1">
          <p className="text-xs text-slate-400">Original Complexity</p>
          <p className="font-semibold text-slate-100">{originalComplexity}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-3 md:col-span-1">
          <p className="text-xs text-slate-400">Optimized Complexity</p>
          <p className={`font-semibold ${stats.complexityImproved ? "text-emerald-300" : "text-slate-100"}`}>{optimizedComplexity}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-3 md:col-span-1">
          <p className="text-xs text-slate-400">Original Score</p>
          <p className="font-semibold text-slate-100">{Math.round(originalScore || 0)}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-3 md:col-span-1">
          <p className="text-xs text-slate-400">Optimized Score</p>
          <p className={`font-semibold ${stats.scoreImproved ? "text-emerald-300" : "text-slate-100"}`}>{Math.round(optimizedScore || 0)}</p>
        </div>
        <div className="rounded-xl border border-cyan-500/40 bg-cyan-500/10 p-3 md:col-span-1">
          <p className="text-xs text-cyan-200">Improvement %</p>
          <p className="font-semibold text-cyan-100">{stats.pct >= 0 ? `+${stats.pct}%` : `${stats.pct}%`}</p>
        </div>
      </div>

      <CodeEditor
        title={view === "optimized" ? "Optimized Code" : "Original Code"}
        code={view === "optimized" ? optimizedCode : originalCode}
        language={language}
        onChange={() => {}}
        onLanguageChange={() => {}}
        loading={false}
        showAnalyzeButton={false}
        showLanguageSelect={false}
        readOnly
      />

      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Improvements</p>
        {improvements?.map((item, idx) => (
          <div
            key={`${item}-${idx}`}
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-100"
          >
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}
