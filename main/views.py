from django.db import DatabaseError
from django.shortcuts import render

from wiki.models import WikiPage
from wiki.seed import ensure_seed_pages

def home_view(request):
    main_doc = {"title": "대문", "content": "스티븐 위키에 오신 것을 환영합니다."}  # 기본 가짜 값
    ensure_seed_pages()

    try:
        page = WikiPage.objects.filter(title="대문").first()
    except DatabaseError:
        page = None

    if page:
        main_doc = {"title": page.title, "content": page.content}
    else:
        try:
            from pymongo import MongoClient

            client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=200)
            db = client["minecraft"]
            wiki_collection = db["wiki"]
            doc = wiki_collection.find_one({"title": "대문"})
            if doc:
                main_doc = {
                    "title": doc.get("title", "대문"),
                    "content": doc.get("content", main_doc["content"]),
                }
        except Exception:
            pass  # DB 연결 실패해도 가짜 데이터로 진행

    return render(request, "main/home.html", {"main_doc": main_doc})

def notice(request):
    notices = [
        {
            'date': '2025-01-15',
            'title': '서버 점검 안내',
            'content': '오늘 23:00~23:30 서버 점검으로 인한 서비스 중단이 예정되어 있습니다.',
            'important': True
        },
        {
            'date': '2025-01-10',
            'title': '위키 편집 가이드 업데이트',
            'content': '새로운 편집 가이드가 업데이트되었습니다. 모든 사용자는 확인해주세요.',
            'important': False
        },
        {
            'date': '2025-01-05',
            'title': '새로운 기능 추가',
            'content': '챗봇 기능이 추가되었습니다. 마인크래프트 관련 질문을 자유롭게 해보세요.',
            'important': False
        }
    ]
    return render(request, "main/notice.html", {'notices': notices})

def tutorial(request):
    tutorials = [
        {
            'title': '위키 문서 작성 규칙',
            'content': '위키 문서를 작성할 때 지켜야 할 기본 규칙들을 안내합니다.',
            'steps': [
                '검색 가능한 제목을 사용하세요',
                '변경 사유(커밋 메시지)를 간단히 기록하세요',
                '금칙어나 저작권에 주의하세요',
                '다른 사용자와 협력하여 작성하세요'
            ]
        },
        {
            'title': '마크다운 사용법',
            'content': '위키에서 사용할 수 있는 마크다운 문법을 설명합니다.',
            'steps': [
                '**굵은 글씨**는 **로 감싸세요',
                '*기울임*은 *로 감싸세요',
                '## 제목은 ##로 시작하세요',
                '[링크](URL)는 []()로 작성하세요'
            ]
        },
        {
            'title': '이미지 업로드 방법',
            'content': '위키에 이미지를 업로드하는 방법을 안내합니다.',
            'steps': [
                '이미지 업로드 버튼을 클릭하세요',
                '적절한 파일명을 사용하세요',
                '저작권에 주의하세요',
                '이미지 설명을 추가하세요'
            ]
        }
    ]
    return render(request, "main/tutorial.html", {'tutorials': tutorials})

def discussion(request):
    discussions = [
        {
            'title': '철 광석 평균 깊이 논쟁',
            'author': 'Miner123',
            'date': '2025-01-15 11:20',
            'replies': 15,
            'last_activity': '2025-01-15 14:30',
            'category': '광물',
            'status': 'active',
            'link': '/wiki/discussions/'
        },
        {
            'title': '참나무 vs 자작나무 건축',
            'author': 'Builder456',
            'date': '2025-01-15 09:10',
            'replies': 8,
            'last_activity': '2025-01-15 12:45',
            'category': '건축',
            'status': 'active',
            'link': '/wiki/discussions/'
        },
        {
            'title': '인챈트 테이블 최적 배치',
            'author': 'Enchanter789',
            'date': '2025-01-14 16:30',
            'replies': 22,
            'last_activity': '2025-01-15 10:15',
            'category': '인챈트',
            'status': 'hot',
            'link': '/wiki/discussions/'
        },
        {
            'title': '네더 요새 찾기 팁',
            'author': 'NetherExplorer',
            'date': '2025-01-14 14:20',
            'replies': 12,
            'last_activity': '2025-01-15 08:45',
            'category': '네더',
            'status': 'active',
            'link': '/wiki/discussions/'
        }
    ]
    return render(request, "main/discussion.html", {'discussions': discussions})

def history(request):
    recent_changes = [
        {
            'page': '석탄 광석',
            'revision': 'rev3',
            'author': 'WikiEditor',
            'date': '2025-01-15 13:10',
            'summary': 'Y좌표 정보 업데이트',
            'size_change': '+150'
        },
        {
            'page': '철 광석',
            'revision': 'rev2',
            'author': 'MinerExpert',
            'date': '2025-01-15 12:00',
            'summary': '생성 확률 수정',
            'size_change': '+89'
        },
        {
            'page': '다이아몬드',
            'revision': 'rev5',
            'author': 'DiamondHunter',
            'date': '2025-01-15 10:30',
            'summary': '인챈트 정보 추가',
            'size_change': '+234'
        },
        {
            'page': '네더라이트',
            'revision': 'rev1',
            'author': 'NetherMaster',
            'date': '2025-01-15 09:15',
            'summary': '새 문서 생성',
            'size_change': '+456'
        }
    ]
    return render(request, "main/history.html", {'recent_changes': recent_changes})
