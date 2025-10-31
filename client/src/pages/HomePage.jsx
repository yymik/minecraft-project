import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const HomePage = () => {
  const { user, isAuthenticated } = useAuth();

  return (
    <div className="card">
      <h1 className="page-title">Minecraft Companion</h1>
      {isAuthenticated ? (
        <p>{user.username}님, 오늘도 즐거운 플레이 되세요!</p>
      ) : (
        <p>
          더 많은 기능을 이용하려면 <Link to="/login">로그인</Link> 해주세요.
        </p>
      )}

      <nav style={{ display: "grid", gap: 12, marginTop: 24 }}>
        <Link to="/wiki">위키</Link>
        <Link to="/chatbot">챗봇</Link>
        <Link to="/wiki/editor">문서 작성</Link>
      </nav>
    </div>
  );
};

export default HomePage;
