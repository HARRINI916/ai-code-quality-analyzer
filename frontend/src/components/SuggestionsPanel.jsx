import React from "react";

export default function SuggestionsPanel({ suggestions }) {
  const items = suggestions?.length
    ? suggestions
    : ["Run analysis to get language-specific quality suggestions."];

  return (
    <section className="saas-card">
      <h3 className="section-title">Suggestions</h3>
      <ul className="stack-sm">
        {items.map((item, index) => (
          <li key={`${item}-${index}`} className="suggestion-item">
            <span className="dot" />
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}
