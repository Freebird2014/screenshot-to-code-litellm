import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { Toaster } from "react-hot-toast";
import EvalsPage from "./components/evals/EvalsPage.tsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PairwiseEvalsPage from "./components/evals/PairwiseEvalsPage";
import RunEvalsPage from "./components/evals/RunEvalsPage.tsx";
import BestOfNEvalsPage from "./components/evals/BestOfNEvalsPage.tsx";
import AllEvalsPage from "./components/evals/AllEvalsPage.tsx";
import OpenAIInputComparePage from "./components/evals/OpenAIInputComparePage.tsx";
import LoginPage from "./components/auth/LoginPage.tsx";
import AuthGuard from "./components/auth/AuthGuard.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <AuthGuard>
              <App />
            </AuthGuard>
          }
        />
        <Route
          path="/evals"
          element={
            <AuthGuard>
              <AllEvalsPage />
            </AuthGuard>
          }
        />
        <Route
          path="/evals/single"
          element={
            <AuthGuard>
              <EvalsPage />
            </AuthGuard>
          }
        />
        <Route
          path="/evals/pairwise"
          element={
            <AuthGuard>
              <PairwiseEvalsPage />
            </AuthGuard>
          }
        />
        <Route
          path="/evals/best-of-n"
          element={
            <AuthGuard>
              <BestOfNEvalsPage />
            </AuthGuard>
          }
        />
        <Route
          path="/evals/run"
          element={
            <AuthGuard>
              <RunEvalsPage />
            </AuthGuard>
          }
        />
        <Route
          path="/evals/openai-input-compare"
          element={
            <AuthGuard>
              <OpenAIInputComparePage />
            </AuthGuard>
          }
        />
      </Routes>
    </Router>
    <Toaster toastOptions={{ className: "dark:bg-zinc-950 dark:text-white" }} />
  </React.StrictMode>
);
