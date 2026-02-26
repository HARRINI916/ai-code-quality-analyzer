import React from "react";

export default function MetricsPanel({ metrics }) {
  if (!metrics) return null;

  const items = [
    { label: "Lines of Code", value: metrics.lines_of_code },
    { label: "Number of Functions", value: metrics.functions },
    { label: "Number of Loops", value: metrics.loops },
    { label: "Nesting Depth", value: metrics.nesting_depth },
    { label: "Cyclomatic Complexity", value: metrics.cyclomatic_complexity },
    { label: "Comment Ratio", value: `${Math.round((metrics.comment_ratio || 0) * 100)}%` },
  ];

  return (
    <section className="saas-card">
      <h3 className="section-title">Code Metrics</h3>
      <div className="metrics-grid">
        {items.map((item) => (
          <div key={item.label} className="metric-item">
            <p>{item.label}</p>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
