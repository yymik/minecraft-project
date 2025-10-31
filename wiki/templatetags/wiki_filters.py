from urllib.parse import quote

from django import template
from django.utils.html import escape
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


PIPE_TABLE_RE = re.compile(r"<p>((?:\|.*?\|\s*)+)</p>", re.DOTALL)
IMG_TAG_RE = re.compile(r"(<img[^>]+>)")
SECTION_REMOVE_PATTERNS = [
    re.compile(
        r"<h3[^>]*>\s*아이템\s*관련\s*문서\s*모음.*?(?:</table>|</div>)",
        re.DOTALL,
    )
]


def _build_pipe_table(lines):
    """Convert namu-style pipe blocks into HTML tables with sensible colspans."""
    rows = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        cells = [cell for cell in cells if cell != ""]
        if cells:
            rows.append(cells)

    if not rows:
        return None

    is_recipe = any("[ 조합법" in cell for row in rows for cell in row)
    if is_recipe:
        return _build_recipe_cards(rows)

    max_cols = max(len(row) for row in rows) or 1

    row_html = []
    for cells in rows:
        col_count = len(cells)
        if col_count == 0:
            continue
        cell_html = []
        for idx, cell in enumerate(cells):
            colspan = 1
            if col_count == 1 and max_cols > 1:
                colspan = max_cols
            elif idx == col_count - 1 and col_count < max_cols:
                colspan = max_cols - (col_count - 1)
            if colspan < 1:
                colspan = 1
            colspan_attr = f' colspan="{colspan}"' if colspan > 1 else ""
            cell_html.append(f"<td{colspan_attr}>{cell}</td>")
        row_html.append(f"<tr>{''.join(cell_html)}</tr>")

    classes = ["wiki-table"]
    if is_recipe:
        classes.append("recipe-table")
    class_attr = " ".join(classes)
    return f'<table class="{class_attr}"><tbody>{"".join(row_html)}</tbody></table>'


def _convert_pipe_tables(html: str) -> str:
    """Find <p>| ... |</p> blocks and render them as structured tables."""

    def repl(match: re.Match) -> str:
        block = match.group(1) or ""
        lines = block.splitlines()
        table_html = _build_pipe_table(lines)
        return table_html or match.group(0)

    return PIPE_TABLE_RE.sub(repl, html)


def _strip_unwanted_sections(html: str) -> str:
    """Remove sections that should not appear in rendered wiki pages."""
    cleaned = html
    for pattern in SECTION_REMOVE_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return cleaned


def _cleanup_tokens(tokens):
    cleaned = []
    for token in tokens:
        if not token:
            continue
        if "파일:" in token:
            continue
        cleaned.append(token.strip())
    return [tok for tok in cleaned if tok]


def _parse_recipe_steps(cell_html):
    """Parse a recipe cell into structured step dictionaries."""
    tokens = [seg for seg in IMG_TAG_RE.split(cell_html) if seg]
    tokens = _cleanup_tokens(tokens)
    steps = []
    group_size = 7
    for idx in range(0, len(tokens), group_size):
        group = tokens[idx: idx + group_size]
        if len(group) < group_size:
            break
        board, input_top, input_bottom, xp_icon, xp_value, output_icon, time_text = group[:group_size]
        steps.append({
            "board": board,
            "input_top": input_top,
            "input_bottom": input_bottom,
            "xp_icon": xp_icon,
            "xp_value": xp_value,
            "output_icon": output_icon,
            "time_text": time_text,
        })
    return steps


def _render_recipe_step(step):
    """Construct HTML for a single crafting/smelting step."""
    xp_value = escape(step["xp_value"])
    time_text = escape(step["time_text"])
    return (
        '<div class="recipe-step">'
        f'<div class="recipe-step__board">{step["board"]}'
        f'<span class="recipe-step__slot recipe-step__slot--input">{step["input_top"]}</span>'
        f'<span class="recipe-step__slot recipe-step__slot--fuel">{step["input_bottom"]}</span>'
        f'<span class="recipe-step__slot recipe-step__slot--output">{step["output_icon"]}</span>'
        '</div>'
        f'<div class="recipe-step__meta">'
        f'<span class="recipe-step__xp">{step["xp_icon"]}'
        f'<span class="recipe-step__xp-value">{xp_value}</span>'
        '</span>'
        f'<span class="recipe-step__time">{time_text}</span>'
        '</div>'
        '</div>'
    )


def _build_recipe_cards(rows):
    """Render recipe-style pipe tables into rich crafting cards."""
    if not rows:
        return None

    title_html = ""
    thumb_html = ""
    meta_rows = []
    recipe_entries = []

    idx = 0
    if idx < len(rows) and len(rows[idx]) == 1:
        title_html = rows[idx][0]
        idx += 1

    if idx < len(rows) and len(rows[idx]) == 1 and "<img" in rows[idx][0]:
        thumb_html = rows[idx][0]
        idx += 1

    for row in rows[idx:]:
        if any("[ 조합법" in cell for cell in row):
            continue
        if len(row) == 2 and not any("<img" in cell for cell in row):
            meta_rows.append(row)
            continue
        if len(row) >= 2:
            label = row[0]
            content_html = " ".join(row[1:])
            steps = _parse_recipe_steps(content_html)
            if steps:
                recipe_entries.append((label, steps))

    parts = ['<div class="recipe-card">']
    if title_html:
        parts.append(f'<div class="recipe-card__title">{title_html}</div>')
    if thumb_html:
        parts.append(f'<div class="recipe-card__thumb">{thumb_html}</div>')
    if meta_rows:
        parts.append('<dl class="recipe-card__meta">')
        for key, value in meta_rows:
            parts.append(f"<dt>{key}</dt><dd>{value}</dd>")
        parts.append("</dl>")
    for label, steps in recipe_entries:
        step_html = "".join(_render_recipe_step(step) for step in steps)
        parts.append(
            '<div class="recipe-card__entry">'
            f'<div class="recipe-card__entry-label">{label}</div>'
            f'<div class="recipe-card__entry-body">{step_html}</div>'
            '</div>'
        )
    parts.append("</div>")
    return "".join(parts)


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

    rendered = _convert_pipe_tables(rendered)
    rendered = _strip_unwanted_sections(rendered)
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


@register.filter(name="unique")
def unique(sequence):
    """리스트에서 중복을 제거하고 원래 순서를 유지."""
    if not sequence:
        return []
    seen = set()
    result = []
    for item in sequence:
        key = str(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result

