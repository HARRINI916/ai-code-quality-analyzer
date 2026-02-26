import React from "react";

const scoreColors = {
  readability: "bar-sky",
  maintainability: "bar-emerald",
  efficiency: "bar-amber",
  safety: "bar-rose",
};

export default function ScoreBreakdown({ scores }) {
  if (!scores) return null;

  const categories = ["readability", "maintainability", "efficiency", "safety"];

  return (
    <section className="saas-card">
      <div className="score-head">
        <h3>Score Breakdown</h3>
        <div className="score-overall">
          Overall {Math.round(scores.overall)}
        </div>
      </div>

      <div className="stack-sm">
        {categories.map((key) => {
          const value = Math.round(scores[key] || 0);
          return (
            <div key={key} className="score-row">
              <div className="score-meta">
                <span className="capitalize">{key}</span>
                <span>{value}/100</span>
              </div>
              <div className="score-track">
                <div
                  className={`score-fill ${scoreColors[key]}`}
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
