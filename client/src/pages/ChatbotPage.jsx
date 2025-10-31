import React, { useState } from "react";
import { apiClient } from "../api/client.js";

const ChatbotPage = () => {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  const pushMessage = (role, content) => {
    setMessages((prev) => [...prev, { role, content, ts: Date.now() }]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!text.trim()) return;

    const userText = text.trim();
    pushMessage("user", userText);
    setText("");
    setError("");

    try {
      const { data } = await apiClient.post("chatbot/messages/", {
        message: userText
      });
      pushMessage("bot", data.reply || "(응답이 없습니다)");
    } catch (err) {
      setError(err.response?.data?.detail || "챗봇 호출에 실패했습니다.");
    }
  };

  return (
    <div className="card" style={{ maxWidth: 720, margin: "0 auto" }}>
      <h1 className="page-title">Minecraft 챗봇</h1>
      <div
        style={{
          background: "#f8fafc",
          borderRadius: 12,
          padding: 16,
          minHeight: 320,
          marginBottom: 16,
          display: "grid",
          gap: 12
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.ts}
            style={{
              justifySelf: msg.role === "user" ? "end" : "start",
              background: msg.role === "user" ? "#2563eb" : "#e2e8f0",
              color: msg.role === "user" ? "#fff" : "#1f2937",
              padding: "10px 14px",
              borderRadius: 10,
              maxWidth: "80%"
            }}
          >
            {msg.content}
          </div>
        ))}
        {!messages.length && <p>질문을 입력하면 Dialogflow가 답변합니다.</p>}
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 12 }}>
        <input
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="예: 엔더 드래곤 준비는 어떻게 해?"
          style={{ flex: 1 }}
        />
        <button type="submit">전송</button>
      </form>
      {error && <p style={{ color: "#ef4444", marginTop: 12 }}>{error}</p>}
    </div>
  );
};

export default ChatbotPage;
