import React from "react";
import Editor from "@monaco-editor/react";

const languageMap = {
  python: "python",
  c: "c",
  cpp: "cpp",
  java: "java",
  javascript: "javascript",
  go: "go",
};

export default function MonacoPanel({ title, code, language, onChange, readOnly = false, height = "340px" }) {
  return (
    <section className="saas-card">
      <div className="saas-card-header">
        <h3>{title}</h3>
      </div>
      <div className="editor-shell">
        <Editor
          height={height}
          language={languageMap[language] || "python"}
          theme="vs-light"
          value={code}
          onChange={(value) => onChange?.(value || "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            automaticLayout: true,
            scrollBeyondLastLine: false,
            readOnly,
          }}
        />
      </div>
    </section>
  );
}
