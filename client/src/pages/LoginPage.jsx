import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    const result = await login(form);
    if (result.ok) {
      navigate("/");
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 400, margin: "0 auto" }}>
      <h1 className="page-title">로그인</h1>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        <label>
          아이디
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            required
            autoFocus
          />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        {error && <p style={{ color: "#ef4444" }}>{error}</p>}
        <button type="submit">로그인</button>
      </form>
      <p style={{ marginTop: 16 }}>
        아직 계정이 없으신가요? <Link to="/register">회원가입</Link>
      </p>
    </div>
  );
};

export default LoginPage;
