from types import SimpleNamespace
import re

from django.contrib import messages
from django.db import DatabaseError
from django.db.models import Case, F, IntegerField, Q, When
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from datetime import datetime
from urllib.parse import unquote
from bson import ObjectId
from bson.errors import InvalidId

from markdown import markdown

from .models import WikiPage
from .seed import ensure_seed_pages
from .opennamu_client import get_opennamu_client
from .templatetags import wiki_filters


#MARKDOWN -> HTML 변환
# wiki/views.py
from django.shortcuts import render, get_object_or_404
from markdown import markdown
from .models import WikiPage 

def page_detail(request, slug):
    page = get_object_or_404(WikiPage, slug=slug)
    # 마크다운 → HTML (표/리스트 확장 포함)
    page_html = markdown(page.content, extensions=['extra', 'tables', 'sane_lists'])
    return render(request, 'wiki/page_detail.html', {
        'page': page,
        'page_html': page_html,
    })

def detail(request, slug):
    page = get_object_or_404(WikiPage, slug=slug)

    # ⬇︎ 마크다운 원문 필드 선택(프로젝트에 맞게 자동 선택)
    raw = getattr(page, "content_md", None) or getattr(page, "content", None) or getattr(page, "body", "")
    page_html = markdown(raw, extensions=['extra', 'tables', 'sane_lists'])

    return render(request, 'wiki/detail.html', {
        'page': page,
        'page_html': page_html,
    })


CATEGORY_DEFINITIONS = {
    "trade": {
        "label": "거래",
        "description": "주민과의 거래, 경제 시스템, 에메랄드 수급과 관련된 문서를 모았습니다.",
        "category_filters": ["거래"],
        "tag_keywords": ["거래", "에메랄드", "주민", "경제"],
    },
    "brewing": {
        "label": "양조",
        "description": "물약 제작과 양조 시스템, 재료 수급 팁을 확인하세요.",
        "category_filters": ["양조"],
        "tag_keywords": ["물약", "양조", "팁"],
    },
    "mobs": {
        "label": "몹",
        "description": "각종 몹의 행동 패턴과 공략 방법을 정리했습니다.",
        "category_filters": ["몹"],
        "tag_keywords": ["몹", "전투", "드롭"],
    },
    "blocks": {
        "label": "블록",
        "description": "건축과 채굴에 도움이 되는 블록 및 구조물 정보를 모았습니다.",
        "category_filters": ["블록", "광물", "구조물"],
        "tag_keywords": ["블록", "구조물", "건축", "채굴"],
    },
    "items": {
        "label": "아이템",
        "description": "무기, 도구, 장비 등 주요 아이템 정보를 한눈에 살펴보세요.",
        "category_filters": ["아이템"],
        "tag_keywords": ["아이템", "무기", "도구", "장비"],
    },
}

SAMPLE_QUESTIONS = [
    {
        "_id": "sample-qa-1",
        "title": "엔더 드래곤 공략 준비는 어떻게 해야 하나요?",
        "author": "DragonHunter",
        "created_at": "2025-01-10 13:20",
        "content": (
            "다이아몬드 장비는 준비했지만 엔더 드래곤을 처음 상대합니다. "
            "필수 물약과 아이템 구성, 그리고 추천 전투 루틴이 있을까요?"
        ),
        "answers": [
            {
                "author": "Admin",
                "content": "힘/재생/치유 물약과 침대 폭발 전략을 추천합니다. "
                           "엔더맨 대비용 호박과 물 양동이도 챙기세요.",
                "timestamp": "2025-01-10 14:05",
            },
            {
                "author": "Builder",
                "content": "기둥 파괴를 위해 눈덩이나 활을 준비하고, "
                           "낙하 피해 대비 느린 낙하 물약도 가져가면 편합니다.",
                "timestamp": "2025-01-10 16:12",
            },
        ],
    },
    {
        "_id": "sample-qa-2",
        "title": "위키 문서 수정 시 검수 절차가 있을까요?",
        "author": "WikiNewbie",
        "created_at": "2025-01-08 09:40",
        "content": "규칙 문서를 읽었는데도 검수 절차가 헷갈립니다. "
                   "초보 편집자가 알아야 할 단계가 무엇인지 알려주세요.",
        "answers": [
            {
                "author": "Moderator",
                "content": "간단한 수정은 바로 적용되고, 큰 변경 사항은 토론을 통해 합의 후 반영하면 됩니다. "
                           "요약란에 변경 이유를 간단히 적어 주세요.",
                "timestamp": "2025-01-08 10:15",
            }
        ],
    },
]

opennamu_client = get_opennamu_client()

DEFAULT_RELATED = [
    "건축 블록",
    "색깔 블록",
    "자연 블록",
    "기능 블록",
    "레드스톤 블록",
    "전투",
    "음식 및 음료",
    "도구 및 유용한 물건",
]


def _override_display_title(raw_title: str) -> str:
    if raw_title == "마인크래프트/아이템/재료":
        return "아이템/재료"
    return raw_title


def _override_content_heading(content: str, original_title: str) -> str:
    if not content or original_title != "마인크래프트/아이템/재료":
        return content
    return content.replace("# 마인크래프트/아이템/재료", "# 아이템/재료", 1)


def _strip_edit_markers(content: str) -> str:
    if not content:
        return content
    return re.sub(r"\s*\[편집\]", "", content)


def _render_page_html(raw_content: str) -> str:
    """Convert stored wiki markup into HTML once at the view layer."""
    rendered = wiki_filters.wiki_links(raw_content or "")
    return wiki_filters.markdown_to_html(rendered)


def _dedupe_preserve_order(items):
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        yield item


WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


def _extract_wiki_titles(raw: str):
    if not raw:
        return []
    titles = []
    for match in WIKILINK_PATTERN.finditer(str(raw)):
        candidate = match.group(1)
        if not candidate:
            continue
        if "|" in candidate:
            candidate = candidate.split("|", 1)[0]
        candidate = candidate.split("#", 1)[0].strip()
        if not candidate or candidate.startswith(("http", "#")):
            continue
        titles.append(candidate)
    return list(_dedupe_preserve_order(titles))


def _build_related_titles(raw_content: str, category: str, current_title: str):
    if current_title == "마인크래프트/아이템/재료":
        return DEFAULT_RELATED

    candidates = _extract_wiki_titles(raw_content)
    related = list(candidates[:8])

    if len(related) >= 8:
        return related

    fallback_pool = DEFAULT_RELATED

    for candidate in fallback_pool:
        if candidate in related or candidate == current_title:
            continue
        related.append(candidate)
        if len(related) >= 8:
            break

    return related


def _serialize_question(doc, include_answers=False):
    if not doc:
        return None
    data = dict(doc)
    if "_id" in data:
        data["id"] = str(data["_id"])
        data["_id"] = str(data["_id"])
    created = data.get("created_at")
    if isinstance(created, datetime):
        data["created_at"] = created.strftime("%Y-%m-%d %H:%M")
    if include_answers:
        answers = []
    for answer in data.get("answers", []):
        a = dict(answer)
        ts = a.get("timestamp")
        if isinstance(ts, datetime):
            a["timestamp"] = ts.strftime("%Y-%m-%d %H:%M")
            answers.append(a)
        data["answers"] = answers
    return data

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]
wiki = db["wiki"]

# Ensure index for fast lookup and uniqueness on title
try:
    wiki.create_index("title", unique=True)
except Exception:
    # Avoid raising on startup if index exists or Mongo unavailable in some contexts
    pass


# MongoDB 기반 문서 보기
def _decode_title(value: str) -> str:
    """Return a human‑readable title decoded from the URL component."""
    if not value:
        return value
    decoded = unquote(value)
    return decoded or value


def _title_candidates(raw_title: str):
    """Yield possible title variants for lookups (decoded → raw)."""
    decoded = _decode_title(raw_title)
    if decoded:
        yield decoded
    if raw_title and raw_title != decoded:
        yield raw_title


def wiki_detail_view(request, title):
    ensure_seed_pages()

    decoded_title = _decode_title(title)
    title_candidates = list(_title_candidates(title))

    if opennamu_client.enabled:
        remote = opennamu_client.fetch_page(title)
        if not remote and decoded_title != title:
            remote = opennamu_client.fetch_page(decoded_title)
        if remote:
            meta = remote.get("metadata") if isinstance(remote.get("metadata"), dict) else {}
            tags = meta.get("tags", [])
            if not isinstance(tags, str):
                tags = ",".join(tags) if isinstance(tags, (list, tuple)) else ""
            page_stub = SimpleNamespace(
                category=meta.get("category", "기타"),
                view_count=meta.get("view_count", 0),
                tags=tags,
                author=meta.get("last_editor", "익명"),
                updated_at=remote.get("updated_at", datetime.utcnow()),
            )
            remote_title = remote.get("title") or decoded_title or title
            raw_content = remote.get("content", "")
            content = _strip_edit_markers(_override_content_heading(raw_content, remote_title))
            display_title = _override_display_title(remote_title)
            return render(request, "wiki/detail.html", {
                "title": display_title,
                "content": content,
                "page_html": _render_page_html(content),
                "page": page_stub,
                "related_titles": _build_related_titles(content, page_stub.category, remote_title),
            })

    try:
        page = None
        for candidate in title_candidates:
            page = WikiPage.objects.filter(title=candidate).first()
            if page:
                break
    except DatabaseError:
        page = None

    if page:
        try:
            WikiPage.objects.filter(pk=page.pk).update(view_count=F("view_count") + 1)
            page.refresh_from_db(fields=["view_count", "updated_at"])
        except DatabaseError:
            pass
        display_title = _override_display_title(page.title)
        content = _strip_edit_markers(_override_content_heading(page.content, page.title))
        return render(request, "wiki/detail.html", {
            "title": display_title,
            "content": content,
            "page_html": _render_page_html(content),
            "page": page,
            "related_titles": _build_related_titles(content, page.category, page.title),
        })

    doc = None
    try:
        for candidate in title_candidates:
            doc = wiki.find_one({"title": candidate})
            if doc:
                break
    except (PyMongoError, ServerSelectionTimeoutError):
        doc = None

    if doc:
        tags = doc.get("tags") or ""
        if isinstance(tags, list):
            tags = ",".join(tags)
        page_stub = SimpleNamespace(
            category=doc.get("category", "기타"),
            view_count=doc.get("view_count", 0),
            tags=tags,
            author=doc.get("last_editor", "익명"),
            updated_at=doc.get("updated_at", datetime.utcnow()),
        )
        resolved_title = doc.get("title") or decoded_title or title
        raw_content = doc.get("content", "")
        content = _strip_edit_markers(_override_content_heading(raw_content, resolved_title))
        display_title = _override_display_title(resolved_title)
        return render(request, "wiki/detail.html", {
            "title": display_title,
            "content": content,
            "page_html": _render_page_html(content),
            "page": page_stub,
            "related_titles": _build_related_titles(content, page_stub.category, resolved_title),
        })

    return render(request, "wiki/not_found.html", {"title": decoded_title or title})


# 메인(네비게이션) 뷰
def wiki_main(request):
    ensure_seed_pages()
    return render(request, "wiki/main.html")


# MongoDB 기반 문서 편집
def wiki_edit_view(request, title):
    decoded_title = _decode_title(title)
    title_candidates = list(_title_candidates(title))

    if opennamu_client.enabled:
        remote_doc = opennamu_client.fetch_page(title) or {}
        if not remote_doc and decoded_title != title:
            remote_doc = opennamu_client.fetch_page(decoded_title) or {}
        if request.method == "POST":
            new_content = request.POST.get("content", "")
            summary = request.POST.get("summary", "")
            success = opennamu_client.push_page(title, new_content, summary)
            if success:
                messages.success(request, "openNAMU 문서를 저장했습니다.")
                return redirect("wiki:wiki_detail", title=title)
            messages.error(request, "openNAMU 저장에 실패했습니다. 관리자에게 문의하세요.")
        return render(request, "wiki/edit.html", {
            "title": remote_doc.get("title") or decoded_title or title,
            "content": remote_doc.get("content", ""),
        })

    doc = None
    for candidate in title_candidates:
        doc = wiki.find_one({"title": candidate})
        if doc:
            break

    if request.method == "POST":
        new_content = request.POST.get("content", "")
        summary = request.POST.get("summary", "")
        now = datetime.utcnow()

        wiki.update_one(
            {"title": title},
            {
                "$set": {
                    "content": new_content,
                    "updated_at": now,
                    "last_editor": "admin"
                },
                "$push": {
                    "history": {
                        "editor": "admin",
                        "timestamp": now,
                        "summary": summary,
                        "content": new_content
                    }
                }
            },
            upsert=True
        )
        return redirect("wiki:wiki_detail", title=title)

    return render(request, "wiki/edit.html", {
        "title": doc.get("title") if doc else decoded_title or title,
        "content": doc["content"] if doc else "",
    })


# 문서 내용 일부만 렌더 (부분 갱신 용도)
def wiki_detail_partial(request, title):
    ensure_seed_pages()

    decoded_title = _decode_title(title)
    title_candidates = list(_title_candidates(title))

    try:
        page = None
        for candidate in title_candidates:
            page = WikiPage.objects.filter(title=candidate).first()
            if page:
                break
    except DatabaseError:
        page = None

    if page:
        return render(request, "wiki/detail_partial.html", {
            "title": page.title,
            "content": page.content,
        })

    doc = None
    try:
        for candidate in title_candidates:
            doc = wiki.find_one({"title": candidate})
            if doc:
                break
    except (PyMongoError, ServerSelectionTimeoutError):
        doc = None

    if doc:
        return render(request, "wiki/detail_partial.html", {
            "title": doc.get("title", title),
            "content": doc.get("content", ""),
        })

    return render(request, "wiki/not_found.html", {"title": title})


# 위키 검색 기능
def wiki_search(request):
    ensure_seed_pages()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "relevance")
    category = request.GET.get("category", "")
    
    if not query:
        return render(request, "wiki/search.html", {
            "query": "",
            "results": [],
            "sort": sort,
            "category": category
        })
    
    try:
        # Django ORM을 사용한 검색
        # 기본 검색 쿼리
        search_query = WikiPage.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )
        
        # 카테고리 필터
        if category:
            search_query = search_query.filter(category=category)
        
        # 정렬
        if sort == "date":
            search_query = search_query.order_by('-updated_at')
        elif sort == "views":
            search_query = search_query.order_by('-view_count')
        else:  # relevance
            # 제목에 정확히 일치하는 것을 먼저, 그 다음 부분 일치
            search_query = search_query.annotate(
                relevance=Case(
                    When(title__iexact=query, then=1),
                    When(title__icontains=query, then=2),
                    default=3,
                    output_field=IntegerField()
                )
            ).order_by('relevance', '-updated_at')
        
        results = search_query[:50]  # 최대 50개 결과
        
        return render(request, "wiki/search.html", {
            "query": query,
            "results": results,
            "sort": sort,
            "category": category,
            "total_count": results.count() if hasattr(results, 'count') else len(results)
        })
        
    except Exception as e:
        # MongoDB 백업 검색
        try:
            cursor = wiki.find({"title": {"$regex": query, "$options": "i"}}, {"title": 1}).limit(20)
            results = [{"title": doc.get("title", ""), "content": "", "category": "기타"} for doc in cursor]
            return render(request, "wiki/search.html", {
                "query": query,
                "results": results,
                "sort": sort,
                "category": category,
                "total_count": len(results)
            })
        except:
            return render(request, "wiki/search.html", {
                "query": query,
                "results": [],
                "sort": sort,
                "category": category,
                "total_count": 0
            })


# 최근 변경 - 페이지 히스토리 기준 최신 N개
def recent_changes(request):
    limit = int(request.GET.get("limit", 30))
    changes = []
    for doc in wiki.find({}, {"title": 1, "history": 1, "updated_at": 1}).limit(500):
        for h in (doc.get("history") or []):
            changes.append({
                "title": doc.get("title"),
                "editor": h.get("editor", "unknown"),
                "timestamp": h.get("timestamp"),
                "summary": h.get("summary", ""),
            })
        # 포함된 히스토리가 없더라도 updated_at 으로 기본 변경 한 건 추가 가능 (옵션)
    # 최신순 정렬
    changes.sort(key=lambda x: x.get("timestamp") or datetime.min, reverse=True)
    changes = changes[:limit]
    return render(request, "wiki/recent_changes.html", {"changes": changes})


# 최근 토론: 간단한 토픽/댓글 모델 (Mongo: discussions)
discussions = db["discussions"]


def recent_discussions(request):
    load_error = None
    topics = []
    try:
        cursor = discussions.find(
            {},
            {"title": 1, "created_at": 1, "last_commented_at": 1}
        ).sort([("last_commented_at", -1), ("created_at", -1)]).limit(50)
        topics = [
            {
                "topic_id": str(doc.get("_id")),
                "title": doc.get("title"),
                "created_at": doc.get("created_at"),
                "last_commented_at": doc.get("last_commented_at"),
            }
            for doc in cursor
        ]
    except (PyMongoError, ServerSelectionTimeoutError):
        load_error = "토론 목록을 불러올 수 없습니다. 잠시 후 다시 시도해주세요."
    return render(request, "wiki/discussions_list.html", {"topics": topics, "load_error": load_error})


def discussion_detail(request, topic_id):
    load_error = None
    try:
        object_id = ObjectId(topic_id)
    except InvalidId:
        return render(request, "wiki/not_found.html", {"title": "토론"})
    try:
        topic = discussions.find_one({"_id": object_id})
    except (PyMongoError, ServerSelectionTimeoutError):
        topic = None
        load_error = "토론 데이터를 불러오는 중 문제가 발생했습니다."

    if not topic:
        return render(request, "wiki/not_found.html", {"title": "토론", "load_error": load_error})

    if request.method == "POST":
        author = request.POST.get("author", "익명")
        content = request.POST.get("content", "").strip()
        now = datetime.utcnow()
        if content:
            try:
                discussions.update_one(
                    {"_id": object_id},
                    {
                        "$push": {"comments": {"author": author, "content": content, "timestamp": now}},
                        "$set": {"last_commented_at": now}
                    }
                )
            except (PyMongoError, ServerSelectionTimeoutError):
                load_error = "댓글을 저장하지 못했습니다. 잠시 후 다시 시도해주세요."
                comments = topic.get("comments") or []
                return render(request, "wiki/discussions_detail.html", {
                    "topic": topic,
                    "comments": comments,
                    "load_error": load_error,
                })
        return redirect("wiki:discussion_detail", topic_id=topic_id)

    comments = topic.get("comments") or []
    return render(request, "wiki/discussions_detail.html", {"topic": topic, "comments": comments, "load_error": load_error})


def discussion_new(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "익명")
        content = request.POST.get("content", "").strip()
        now = datetime.utcnow()
        if title and content:
            res = discussions.insert_one({
                "title": title,
                "author": author,
                "created_at": now,
                "last_commented_at": now,
                "comments": [
                    {"author": author, "content": content, "timestamp": now}
                ]
            })
            return redirect("wiki:discussion_detail", topic_id=str(res.inserted_id))
    return render(request, "wiki/discussions_new.html")


def wiki_category_overview(request, category_slug):
    ensure_seed_pages()
    definition = CATEGORY_DEFINITIONS.get(category_slug)
    if not definition:
        return render(request, "wiki/not_found.html", {"title": "카테고리"})

    try:
        queryset = WikiPage.objects.all()
    except DatabaseError:
        queryset = WikiPage.objects.none()

    filters = Q()
    for cat in definition.get("category_filters", []):
        filters |= Q(category__iexact=cat)
    for keyword in definition.get("tag_keywords", []):
        filters |= (
            Q(tags__icontains=keyword)
            | Q(title__icontains=keyword)
            | Q(summary__icontains=keyword)
        )

    if filters:
        try:
            pages = queryset.filter(filters).distinct().order_by("title")
        except DatabaseError:
            pages = []
    else:
        pages = []

    grouped = {}
    for page in pages:
        grouped.setdefault(page.category or "기타", []).append(page)

    grouped_pages = [
        {"category": category_name, "pages": sorted(pages_in_cat, key=lambda p: p.title)}
        for category_name, pages_in_cat in sorted(grouped.items())
    ]

    navigation = [
        {"slug": slug, "label": info["label"]}
        for slug, info in CATEGORY_DEFINITIONS.items()
    ]

    context = {
        "definition": definition,
        "grouped_pages": grouped_pages,
        "navigation": navigation,
        "current_slug": category_slug,
    }
    return render(request, "wiki/category_overview.html", context)


def wiki_all_pages(request):
    ensure_seed_pages()
    try:
        pages = WikiPage.objects.order_by("title").all()
        total_count = pages.count()
    except DatabaseError:
        pages = []
        total_count = 0

    return render(request, "wiki/all_pages.html", {"pages": pages, "total_count": total_count})


# 문의/연락처 폼 저장
contacts = db["contacts"]


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "익명").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if message:
            contacts.insert_one({
                "name": name,
                "email": email,
                "message": message,
                "created_at": datetime.utcnow(),
            })
            return render(request, "wiki/contact.html", {"success": True})
    return render(request, "wiki/contact.html")


# 운영진 모집 폼 저장
recruits = db["recruits"]


def recruit_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        role = request.POST.get("role", "").strip()
        intro = request.POST.get("intro", "").strip()
        if name and role:
            recruits.insert_one({
                "name": name,
                "role": role,
                "intro": intro,
                "created_at": datetime.utcnow(),
            })
            return render(request, "wiki/recruit.html", {"success": True})
    return render(request, "wiki/recruit.html")


# 질문 게시판 (리스트/상세/작성)
questions = db["questions"]


def qa_list(request):
    sample_mode = False
    try:
        raw_items = list(
            questions.find({}, {"title": 1, "author": 1, "created_at": 1})
            .sort("created_at", -1)
            .limit(100)
        )
        items = [_serialize_question(doc) for doc in raw_items]
    except (PyMongoError, ServerSelectionTimeoutError):
        items = []

    if not items:
        sample_mode = True
        items = [
            _serialize_question(
                {key: value for key, value in sample.items() if key != "answers"},
                include_answers=False,
            )
            for sample in SAMPLE_QUESTIONS
        ]

    return render(request, "wiki/qa_list.html", {"items": items, "is_sample": sample_mode})


def qa_detail(request, qid):
    sample_mode = False
    item = None
    try:
        item = questions.find_one({"_id": ObjectId(qid)})
    except (InvalidId, PyMongoError, ServerSelectionTimeoutError):
        item = None

    if not item:
        sample = next((sample for sample in SAMPLE_QUESTIONS if sample["_id"] == qid), None)
        if sample:
            sample_mode = True
            item = _serialize_question(sample, include_answers=True)
        else:
            return render(request, "wiki/not_found.html", {"title": "질문"})
    else:
        item = _serialize_question(item, include_answers=True)

    if sample_mode and request.method == "POST":
        messages.info(request, "예시 질문에서는 답변을 작성할 수 없습니다. 실제 질문을 등록해보세요!")
        return redirect("wiki:qa_list")

    if not sample_mode and request.method == "POST":
        author = request.POST.get("author", "익명")
        content = request.POST.get("content", "").strip()
        now = datetime.utcnow()
        if content:
            questions.update_one(
                {"_id": ObjectId(qid)},
                {"$push": {"answers": {"author": author, "content": content, "timestamp": now}}},
            )
        return redirect("wiki:qa_detail", qid=qid)

    return render(request, "wiki/qa_detail.html", {"item": item, "is_sample": sample_mode})


def qa_new(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "익명")
        content = request.POST.get("content", "").strip()
        now = datetime.utcnow()
        if title and content:
            res = questions.insert_one({
                "title": title,
                "author": author,
                "content": content,
                "created_at": now,
                "answers": []
            })
            return redirect("wiki:qa_detail", qid=str(res.inserted_id))
    return render(request, "wiki/qa_new.html")

