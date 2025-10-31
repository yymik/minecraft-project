# namu2opennamu.py
import sys, re, html
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

N= "\n"

def text_only(x):
    return html.unescape(x.get_text(" ", strip=True))

def to_namumark(node):
    if isinstance(node, NavigableString):
        return str(node)

    name = node.name.lower()
    out = ""

    # 제거/무시
    if name in {"script","style","noscript"}:
        return ""

    # 제목
    if name in {"h1","h2","h3","h4","h5","h6"}:
        lvl = int(name[1])
        # namumark: == 제목 ==
        mark = "="*lvl
        return f"{N}{mark} {text_only(node)} {mark}{N}{N}"

    # 굵게/기울임
    if name in {"b","strong"}:
        return f"'''{text_only(node)}'''"
    if name in {"i","em"}:
        return f"''{text_only(node)}''"

    # 링크
    if name == "a":
        href = node.get("href","").strip()
        label = text_only(node) or href
        if not href:
            return label
        # 내부/외부 포맷 단순화
        if href.startswith("/"):
            return f"[[{label}]]"
        return f"[{href} {label}]"

    # 코드
    if name in {"code","kbd"}:
        return f"`{text_only(node)}`"
    if name == "pre":
        code = node.get_text("\n", strip=False)
        return f"{N}```{N}{code.rstrip()}{N}```{N}{N}"

    # 문단
    if name in {"p","div"}:
        inner = "".join(to_namumark(c) for c in node.children)
        inner = re.sub(r"\s+\n", "\n", inner).strip()
        return (inner + N + N) if inner else ""

    # 줄바꿈
    if name in {"br","hr"}:
        return N

    # 목록
    if name in {"ul","ol"}:
        bullet = "*" if name=="ul" else "1."
        lines = []
        for li in node.find_all("li", recursive=False):
            body = "".join(to_namumark(c) for c in li.children).strip()
            # 하위 목록 들여쓰기
            sub = ""
            for child in li.find_all(["ul","ol"], recursive=False):
                sub += "".join(to_namumark(child)).rstrip()
            line = f"{bullet} {body}".rstrip()
            if sub:
                line += N + "\n".join(" " + s for s in sub.splitlines())
            lines.append(line)
        return N + N.join(lines) + N + N

    # 표(간단 변환)
    if name == "table":
        rows = []
        for tr in node.find_all("tr"):
            cells = []
            for td in tr.find_all(["th","td"]):
                cells.append(text_only(td).replace("|","\\|"))
            if cells:
                rows.append("| " + " | ".join(cells) + " |")
        if rows:
            # 헤더 감지
            if node.find("th"):
                return N + rows[0] + N + ("|" + " --- |"* (rows[0].count("|")-1)).strip() + N + N.join(rows[1:]) + N + N
            return N + N.join(rows) + N + N
        return ""

    # 이미지(주소만 보존)
    if name == "img":
        src = node.get("src","")
        alt = node.get("alt","")
        return f"[{src} {alt}]" if src else ""

    # 그 외: 자식 재귀
    return "".join(to_namumark(c) for c in node.children)

def main():
    if len(sys.argv) < 3:
        print("usage: python namu2opennamu.py <url_or_htmlfile> <out.txt>")
        sys.exit(1)

    src, out = sys.argv[1], sys.argv[2]

    if src.lower().startswith("http"):
        resp = requests.get(src, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        html_text = resp.text
        source_note = f"{N}----{N}출처: {src} (요약/가공, CC BY-NC-SA 2.0 KR 준수){N}"
    else:
        html_text = open(src, "r", encoding="utf-8").read()
        source_note = ""

    soup = BeautifulSoup(html_text, "lxml")

    # 본문 후보(나무위키/미디어위키 계열 일반 패턴)
    main_candidates = [
        {"id":"content"},
        {"id":"main-content"},
        {"class_":"wiki-content"},
        {"class_":"mw-parser-output"},
        {}
    ]
    body = None
    for sel in main_candidates:
        body = soup.find(**sel)
        if body: break
    if not body: body = soup.body or soup

    # 불필요 블록 제거
    for css in [
        ".toc", ".navbox", ".ad", ".banner", ".sidebar", ".footnote",
        ".reference", ".mw-editsection"
    ]:
        for t in soup.select(css):
            t.decompose()

    text = to_namumark(body)

    # 공백 정리
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + source_note

    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"saved -> {out}")

if __name__ == "__main__":
    main()
