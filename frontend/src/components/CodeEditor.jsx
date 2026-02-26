import React, { useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";

const languageMap = {
  python: "python",
  c: "c",
  cpp: "cpp",
  java: "java",
  javascript: "javascript",
  go: "go",
};

export default function CodeEditor({
  title,
  code,
  language,
  onChange,
  onLanguageChange,
  onAnalyze,
  onRunTests,
  loading,
  runLoading = false,
  runDisabled = false,
  errorMarker,
  showAnalyzeButton = true,
  showRunTestsButton = false,
  showLanguageSelect = true,
  readOnly = false,
}) {
  const monacoRef = useRef(null);
  const modelRef = useRef(null);

  function handleMount(editor, monaco) {
    monacoRef.current = monaco;
    modelRef.current = editor.getModel();
  }

  useEffect(() => {
    if (!monacoRef.current || !modelRef.current) {
      return;
    }

    if (!errorMarker?.line) {
      monacoRef.current.editor.setModelMarkers(modelRef.current, "analysis", []);
      return;
    }

    monacoRef.current.editor.setModelMarkers(modelRef.current, "analysis", [
      {
        startLineNumber: errorMarker.line,
        endLineNumber: errorMarker.line,
        startColumn: 1,
        endColumn: 120,
        message: errorMarker.message || "Code issue detected",
        severity: monacoRef.current.MarkerSeverity.Error,
      },
    ]);
  }, [errorMarker]);

  return (
    <section className="overflow-hidden rounded-3xl border border-slate-700/60 bg-slate-900/70 shadow-xl shadow-slate-950/40 backdrop-blur-xl">
      <div className="border-b border-slate-700/70 bg-slate-900/80 px-5 py-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-slate-100">{title || "Code Editor"}</h2>
            <p className="text-xs text-slate-400">Syntax-aware, multi-language analysis workspace</p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-cyan-200">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
            Live
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          {showLanguageSelect && (
            <select
              className="rounded-xl border border-slate-600 bg-slate-800/90 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500 focus:ring-2"
              value={language}
              onChange={(event) => onLanguageChange(event.target.value)}
            >
              <option value="python">Python</option>
              <option value="c">C</option>
              <option value="cpp">C++</option>
              <option value="java">Java</option>
              <option value="javascript">JavaScript</option>
              <option value="go">Go</option>
            </select>
          )}
          <p className="text-xs text-slate-500">Tip: paste full functions for stronger optimization signals.</p>
        </div>
      </div>

      <div className="overflow-hidden rounded-none border-t border-slate-700 bg-[#0b1220]">
        <Editor
          height="420px"
          language={languageMap[language] || "python"}
          theme="vs-dark"
          value={code}
          onMount={handleMount}
          onChange={(value) => onChange(value || "")}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            automaticLayout: true,
            padding: { top: 14, bottom: 14 },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            readOnly,
          }}
        />
      </div>

      {(showAnalyzeButton || showRunTestsButton) && (
        <div className="flex flex-wrap items-center justify-end gap-2 border-t border-slate-700/70 bg-slate-900/70 px-5 py-4">
          {showRunTestsButton && (
            <button
              type="button"
              onClick={onRunTests}
              disabled={runDisabled || runLoading}
              className="rounded-xl bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {runLoading ? "Running Tests..." : "Run Tests"}
            </button>
          )}
          {showAnalyzeButton && (
            <button
              type="button"
              onClick={onAnalyze}
              disabled={loading}
              className="rounded-xl bg-cyan-500 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          )}
        </div>
      )}
    </section>
  );
}
