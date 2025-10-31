import React from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";
import WikiPage from "./pages/WikiPage.jsx";
import ChatbotPage from "./pages/ChatbotPage.jsx";

const Header = () => {
  const { isAuthenticated, logout } = useAuth();
  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "16px 32px",
        background: "#111827",
        color: "#f9fafb"
      }}
    >
      <Link to="/">Minecraft Companion</Link>
      <nav style={{ display: "flex", gap: 16, alignItems: "center" }}>
        <Link to="/wiki">위키</Link>
        <Link to="/chatbot">챗봇</Link>
        {isAuthenticated ? (
          <button type="button" onClick={logout}>
            로그아웃
          </button>
        ) : (
          <Link to="/login">로그인</Link>
        )}
      </nav>
    </header>
  );
};

const AppShell = () => (
  <div className="app-shell">
    <Header />
    <main className="app-content">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/wiki" element={<WikiPage />} />
        </Route>
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="*" element={<p>페이지를 찾을 수 없습니다.</p>} />
      </Routes>
    </main>
    <footer style={{ padding: 24, textAlign: "center", color: "#6b7280" }}>
      © {new Date().getFullYear()} Minecraft Companion
    </footer>
  </div>
);

const App = () => (
  <BrowserRouter>
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  </BrowserRouter>
);

export default App;
