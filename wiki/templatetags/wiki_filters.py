from urllib.parse import quote

from django import template
from django.utils.safestring import mark_safe
import re

try:
    import markdown
except Exception:
    markdown = None

register = template.Library()


def _normalize_title(title: str) -> str:
    if title is None:
        return ""
    return str(title).strip()


def _title_to_path(title: str) -> str:
    normalized = _normalize_title(title)
    return quote(normalized, safe="")


def _make_link(title: str) -> str:
    return f'<a href="/wiki/{_title_to_path(title)}/">{title}</a>'


@register.filter(name='autolink_wiki')
def autolink_wiki(value: str) -> str:
    if not value:
        return ''

    text = str(value)

    # [[Title]] 형태 자동 링크
    text = re.sub(r"\[\[([^\]]+)\]\]", lambda m: _make_link(m.group(1).strip()), text)

    # "Title" 형태도 링크 (한국어/영문/숫자/공백/밑줄 조합)
    def quote_repl(m):
        inner = m.group(1).strip()
        return _make_link(inner)

    text = re.sub(r'"([\w\s가-힣_]+)"', quote_repl, text)

    return text


@register.filter(name="wiki_links")
def wiki_links(value: str) -> str:
    """문서 내 위키 링크 마크업([[...]], "..." 등)을 HTML 앵커 태그로 변환."""
    return autolink_wiki(value)


@register.filter(name="wiki_title_path")
def wiki_title_path(title: str) -> str:
    """위키 문서 제목을 URL 경로에 안전하게 사용할 수 있도록 인코딩."""
    return _title_to_path(title)


@register.filter(name="markdown_to_html")
def markdown_to_html(value: str) -> str:
    """간단한 마크다운을 HTML로 변환합니다."""
    if not value:
        return ""

    text = str(value)
    if markdown:
        rendered = markdown.markdown(text, extensions=["extra", "sane_lists"])
    else:
        # 최소한의 폴백: 두 줄 개행은 단락, 한 줄 개행은 <br>
        paragraphs = [p.replace("\n", "<br>") for p in text.split("\n\n")]
        rendered = "".join(f"<p>{p}</p>" for p in paragraphs)
    return mark_safe(rendered)


@register.filter(name="split")
def split(value, delimiter=","):
    if not value:
        return []
    return [part for part in str(value).split(delimiter) if part]


@register.filter(name="strip")
def strip_filter(value: str) -> str:
    return str(value).strip() if value is not None else ""


@register.filter(name="extract_links")
def extract_links(value: str):
    """본문에서 [[링크]] 형태를 추출해 리스트로 반환."""
    if not value:
        return []
    return [match.group(1).strip() for match in re.finditer(r"\[\[([^\]]+)\]\]", str(value))]

