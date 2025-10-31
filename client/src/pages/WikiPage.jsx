import React, { useEffect, useState } from "react";
import { apiClient } from "../api/client.js";
import WikiEditor from "../components/WikiEditor.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const WikiPage = () => {
  const { isAuthenticated } = useAuth();
  const [pages, setPages] = useState([]);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    apiClient
      .get("wiki/")
      .then((response) => {
        setPages(response.data.results || []);
      })
      .catch(() => setStatus("문서 목록을 불러오지 못했습니다."));
  }, []);

  useEffect(() => {
    if (!selected) return;
    apiClient
      .get(`wiki/${encodeURIComponent(selected)}/`)
      .then((response) => {
        setContent(response.data.content || "");
        setStatus("");
      })
      .catch(() => setStatus("문서 내용을 불러오지 못했습니다."));
  }, [selected]);

  const handleSave = async () => {
    setStatus("");
    try {
      await apiClient.put(`wiki/${encodeURIComponent(selected)}/`, {
        content
      });
      setStatus("저장했습니다.");
    } catch (error) {
      setStatus(error.response?.data?.detail || "저장에 실패했습니다.");
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 16 }}>
      <aside className="card" style={{ padding: 0, overflow: "hidden" }}>
        <header
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid #e2e8f0",
            fontWeight: 700
          }}
        >
          위키 문서
        </header>
        <nav style={{ maxHeight: "70vh", overflowY: "auto" }}>
          {pages.map((page) => (
            <button
              key={page.title}
              type="button"
              onClick={() => setSelected(page.title)}
              style={{
                width: "100%",
                padding: "12px 20px",
                textAlign: "left",
                border: "none",
                borderBottom: "1px solid #e2e8f0",
                background:
                  selected === page.title ? "rgba(59,130,246,0.12)" : "transparent",
                cursor: "pointer"
              }}
            >
              {page.title}
            </button>
          ))}
        </nav>
      </aside>

      <section className="card" style={{ minHeight: "70vh" }}>
        {selected ? (
          <>
            <header style={{ display: "flex", justifyContent: "space-between" }}>
              <h1 className="page-title">{selected}</h1>
              {isAuthenticated && (
                <button type="button" onClick={handleSave}>
                  저장
                </button>
              )}
            </header>
            {status && <p>{status}</p>}
            {isAuthenticated ? (
              <WikiEditor initialValue={content} onChange={setContent} />
            ) : (
              <article>
                <pre
                  style={{
                    whiteSpace: "pre-wrap",
                    fontFamily: "inherit",
                    lineHeight: 1.5
                  }}
                >
                  {content}
                </pre>
              </article>
            )}
          </>
        ) : (
          <p>왼쪽에서 문서를 선택하세요.</p>
        )}
      </section>
    </div>
  );
};

export default WikiPage;
