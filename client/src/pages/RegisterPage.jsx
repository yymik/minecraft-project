import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
    minecraft_uuid: ""
  });
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (form.password !== form.password2) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }
    const result = await register(form);
    if (result.ok) {
      navigate("/login");
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 500, margin: "0 auto" }}>
      <h1 className="page-title">회원가입</h1>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        <label>
          아이디
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          이메일
          <input name="email" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Minecraft UUID
          <input
            name="minecraft_uuid"
            value={form.minecraft_uuid}
            onChange={handleChange}
            required
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
        <label>
          비밀번호 확인
          <input
            type="password"
            name="password2"
            value={form.password2}
            onChange={handleChange}
            required
          />
        </label>
        {error && <p style={{ color: "#ef4444" }}>{error}</p>}
        <button type="submit">회원가입</button>
      </form>
      <p style={{ marginTop: 16 }}>
        이미 계정이 있으신가요? <Link to="/login">로그인</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
