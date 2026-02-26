import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || "/api";
const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");

const api = axios.create({
  baseURL: API_BASE_URL,
});

export function formatApiError(error, fallbackMessage) {
  const status = error?.response?.status;
  const responseData = error?.response?.data;

  const backendMessage =
    responseData?.message ||
    responseData?.detail ||
    responseData?.error ||
    (status ? "" : `Request failed to reach API at ${API_BASE_URL}. Start backend: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`) ||
    error?.message ||
    fallbackMessage;

  if (status) {
    return `HTTP ${status}: ${backendMessage}`;
  }

  return backendMessage || fallbackMessage;
}

export async function analyze(code, language) {
  const response = await api.post("/analyze", { code, language });
  return response.data;
}

export async function optimize(code, language) {
  const response = await api.post("/optimize", { code, language });
  return response.data;
}

export async function execute(code, language, testCases = []) {
  const response = await api.post("/execute", {
    code,
    language,
    test_cases: testCases,
  });
  return response.data;
}
