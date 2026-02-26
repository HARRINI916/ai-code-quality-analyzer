import React from "react";

export default function BugRiskMeter({ bugProbability }) {
  const safeValue = typeof bugProbability === "number" ? bugProbability : 0;
  const percent = Math.round(safeValue * 100);
  const color = percent < 30 ? "#22c55e" : percent < 60 ? "#eab308" : "#ef4444";

  return (
    <section className="panel">
      <h3>Bug Probability</h3>
      <p className="number" style={{ color }}>{percent}%</p>
      <div className="progress-bg">
        <div className="progress-fill" style={{ width: `${percent}%`, background: color }} />
      </div>
    </section>
  );
}
