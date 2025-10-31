import sys, re, html, os, hashlib, pathlib
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

OUT_IMG_DIR = "media/wiki/materials"     # 로컬 저장 경로
PUBLIC_IMG_PREFIX = "/media/wiki/materials/"  # 본문 치환 경로

def sanitize_name(url):
    p = urlparse(url)
    base = os.path.basename(p.path) or "img"
    base = re.sub(r"[^가-힣a-zA-Z0-9._-]+","_", base)
    if not os.path.splitext(base)[1]:
        base += ".png"
    # 충돌 방지 해시
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    stem, ext = os.path.splitext(base)
    return f"{stem}_{h}{ext}"

def fetch(url):
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    return r

def main():
    if len(sys.argv) < 3:
        print("usage: python namu2md_with_images.py <url> <out.md>")
        sys.exit(1)
    src, out_md = sys.argv[1], sys.argv[2]

    html_text = fetch(src).text
    soup = BeautifulSoup(html_text, "lxml")

    # 본문 후보 우선 선택
    body = None
    for sel in [{"class_":"wiki-content"},{"id":"content"},{"class_":"mw-parser-output"}]:
        body = soup.find(**sel)
        if body: break
    if not body: body = soup.body or soup

    # 잡동사니 제거
    for css in [".toc",".navbox",".ad",".banner",".sidebar",".footnote",".reference",".mw-editsection"]:
        for t in soup.select(css):
            t.decompose()

    # 이미지 처리: src 절대경로화 + 다운로드 + 경로 치환(로컬)
    pathlib.Path(OUT_IMG_DIR).mkdir(parents=True, exist_ok=True)
    for img in body.find_all("img"):
        src_url = img.get("src") or ""
        if not src_url or src_url.startswith("data:"):
            img.decompose()
            continue
        abs_url = urljoin(src, src_url)
        try:
            fname = sanitize_name(abs_url)
            path = pathlib.Path(OUT_IMG_DIR, fname)
            if not path.exists():
                r = fetch(abs_url)
                path.write_bytes(r.content)
            img.replace_with(f"![]({PUBLIC_IMG_PREFIX}{fname})")
        except Exception:
            img.decompose()

    # 링크/헤더/인라인 변환: 간단 Markdown
    def node_to_md(node):
        if isinstance(node, NavigableString):
            return str(node)
        name = node.name.lower()
        if name in {"script","style","noscript"}:
            return ""
        if re.match(r"h[1-6]", name):
            lvl = int(name[1])
            return "\n" + ("#"*lvl) + " " + node.get_text(" ", strip=True) + "\n\n"
        if name in {"b","strong"}:
            return f"**{node.get_text(strip=True)}**"
        if name in {"i","em"}:
            return f"*{node.get_text(strip=True)}*"
        if name == "a":
            href = node.get("href","").strip()
            label = node.get_text(strip=True) or href
            if not href: return label
            return f"[{label}]({urljoin(src, href)})"
        if name in {"pre","code"}:
            t = node.get_text("\n", strip=False)
            if name=="pre":
                return f"\n```\n{t.rstrip()}\n```\n\n"
            return f"`{t.strip()}`"
        if name in {"p","div"}:
            inner = "".join(node_to_md(c) for c in node.children).strip()
            return (inner + "\n\n") if inner else ""
        if name in {"br","hr"}:
            return "\n"
        if name in {"ul","ol"}:
            bullet = "-" if name=="ul" else "1."
            lines=[]
            for li in node.find_all("li", recursive=False):
                body = "".join(node_to_md(c) for c in li.children).strip()
                lines.append(f"{bullet} {body}")
            return "\n".join(lines) + "\n\n"
        if name == "table":
            # 간단 테이블 → 파이프 테이블
            rows=[]
            for tr in node.find_all("tr"):
                cells=[c.get_text(" ", strip=True).replace("|","\\|") for c in tr.find_all(["th","td"])]
                if cells: rows.append("| " + " | ".join(cells) + " |")
            if rows:
                if node.find("th"):
                    header=rows[0]
                    cols=header.count("|")-1
                    sep="|"+" --- |"*cols
                    return "\n" + header + "\n" + sep.strip() + "\n" + "\n".join(rows[1:]) + "\n\n"
                return "\n" + "\n".join(rows) + "\n\n"
            return ""
        # 그 외
        return "".join(node_to_md(c) for c in node.children)

    md = node_to_md(body)

    # 상단 메뉴류 잘라내기: 첫 헤더부터
    md = re.split(r"\n#+\s", md, maxsplit=1)
    if len(md) == 2:
        md = "# " + md[1]
    else:
        md = "".join(md)

    # 공백 정리
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    md += f"\n\n----\n출처: {src} (요약/가공, CC BY-NC-SA 2.0 KR)\n"

    pathlib.Path(out_md).write_text(md, encoding="utf-8")
    print(f"saved -> {out_md}")

if __name__ == "__main__":
    main()
