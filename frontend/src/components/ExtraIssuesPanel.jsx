import React from "react";

export default function ExtraIssuesPanel({ issues }) {
  if (!issues?.length) {
    return null;
  }

  return (
    <section className="extra-issues-card">
      <h3 className="section-title">Extra Issues</h3>
      <ul className="stack-sm">
        {issues.map((issue, index) => (
          <li key={`${issue}-${index}`} className="extra-issue-item">
            {issue}
          </li>
        ))}
      </ul>
    </section>
  );
}
