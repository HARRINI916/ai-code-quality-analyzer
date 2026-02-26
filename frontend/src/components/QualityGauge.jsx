import React from "react";

export default function QualityGauge({ score }) {
  const safeScore = typeof score === "number" ? score : 0;
  const color = safeScore >= 75 ? "#22c55e" : safeScore >= 50 ? "#eab308" : "#ef4444";
  const size = 120;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = circumference - (safeScore / 100) * circumference;

  return (
    <section className="panel">
      <h3>Quality Score</h3>
      <div className="gauge-wrap">
        <svg width={size} height={size} className="gauge">
          <circle cx={size / 2} cy={size / 2} r={radius} stroke="var(--panel-border)" strokeWidth={stroke} fill="none" />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={stroke}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={progress}
            strokeLinecap="round"
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        </svg>
        <div className="gauge-value">{Math.round(safeScore)}</div>
      </div>
    </section>
  );
}
