import React from "react";

export default function ComplexityChart({ complexity }) {
  const selected = complexity || "O(1)";

  return (
    <section className="panel">
      <h3>Complexity</h3>
      <div className="badge-row">
        <div className="pill pill-active">{selected}</div>
      </div>
    </section>
  );
}
