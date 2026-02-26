import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import { AnalyzerProvider } from "./context/AnalyzerContext";
import AnalysisPage from "./pages/AnalysisPage";
import OptimizationPage from "./pages/OptimizationPage";
import OriginalCodePage from "./pages/OriginalCodePage";

export default function App() {
  return (
    <BrowserRouter>
      <AnalyzerProvider>
        <div className="app-shell">
          <Navbar />
          <main className="main-container">
            <Routes>
              <Route path="/" element={<OriginalCodePage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/optimize" element={<OptimizationPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </AnalyzerProvider>
    </BrowserRouter>
  );
}
