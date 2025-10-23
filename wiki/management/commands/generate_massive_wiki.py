import math
import random
from typing import Dict, Iterable, List, Sequence

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from wiki.models import WikiCategory, WikiPage
from wiki.data.wiki_content import BASE_ENTRIES, SCENARIO_VARIANTS


User = get_user_model()


KEYWORD_LINKS = (
    ("마인크래프트", "마인크래프트"),
    ("모드", "모드"),
    ("모드팩", "모드팩 개요"),
    ("서버", "서버"),
    ("튜토리얼", "튜토리얼"),
    ("패치", "버전 패치 노트 총람 #1"),
    ("업데이트", "버전 패치 대응 매뉴얼"),
    ("논란", "커뮤니티 논란 대응 백서"),
    ("연대기", "커뮤니티 연대기 종합 #1"),
    ("아이템", "네더라이트 검 운용 매뉴얼"),
    ("장비", "엘리트라 비행 운영 지침"),
    ("레이드", "레이드 운영 전략서"),
    ("교육", "교육 커리큘럼 적용 사례"),
    ("자동화", "자동화 설계 보고서"),
)


ANCHOR_PAGES = (
    {
        "title": "마인크래프트",
        "category": "일반",
        "summary": "마인크래프트의 기본 구조와 확장 가능성을 소개하는 중심 문서.",
        "tags": "마인크래프트,기본정보,샌드박스,탐험",
        "content": (
            "# 마인크래프트\n\n"
            "블록 기반 샌드박스 게임으로, 생존·건축·자동화·커뮤니티 이벤트 등 다양한 플레이 스타일을 지원한다. "
            "바닐라 콘텐츠뿐 아니라 [[모드]], [[모드팩 개요|모드팩]], [[서버 아카이브|서버 운영]] 등을 통해 무한한 확장이 가능하다.\n\n"
            "## 빠른 길잡이\n"
            "- [[튜토리얼]]: 입문자를 위한 단계별 가이드\n"
            "- [[버전 패치 노트 총람 #1]]: 최신 변경 사항 요약\n"
            "- [[커뮤니티 논란 대응 백서]]: 안전한 커뮤니티 운영 지침"
        ),
    },
    {
        "title": "모드팩 개요",
        "category": "모드",
        "summary": "대표적인 모드팩 유형과 선택 기준을 설명하는 문서.",
        "tags": "모드팩,선택가이드,자동화,스토리",
        "content": (
            "# 모드팩 개요\n\n"
            "모드팩은 서로 다른 모드를 묶어 일관된 플레이 경험을 제공하는 콘텐츠 번들이다. "
            "기술 자동화, 스토리형 모험, 하드코어 생존 등 다양한 테마가 있으며 난이도와 목표에 따라 선택해야 한다. "
            "[[튜토리얼 허브 #1]]에서 입문 가이드를, [[자동화 설계 보고서]]에서 고급 운용 정보를 확인할 수 있다."
        ),
    },
    {
        "title": "서버 아카이브",
        "category": "서버",
        "summary": "주요 서버의 시즌별 사건과 정책 변화를 기록한 문서.",
        "tags": "서버,운영,연대기,정책",
        "content": (
            "# 서버 아카이브\n\n"
            "국내외 대표 서버의 운영 이력, 레이드 이벤트, 커뮤니티 정책 변화를 정리했다. "
            "세부 사례는 [[레이드 운영 전략서]]와 [[커뮤니티 논란 대응 백서]]에서 이어서 확인할 수 있다."
        ),
    },
)


def _anchor_content_from_entry(entry: Dict[str, object]) -> str:
    overview = _paragraphs(entry.get("background", []))
    preparation = _bullet(entry.get("preparation", []))
    workflow = _bullet(entry.get("workflow", []))
    advanced = _bullet(entry.get("advanced", []))
    troubleshooting = _bullet(entry.get("troubleshooting", []))
    incidents = _bullet(entry.get("incidents", []))
    community = _bullet(entry.get("community", []))
    patches = _bullet(entry.get("patch_notes", []))
    metrics = _metrics_table(entry.get("metrics", {}))
    references = _reference_section(entry.get("related", []))

    sections = [
        f"# {entry['title']}",
        "## 개요",
        overview,
        "## 준비 사항",
        preparation,
        "## 운용 절차",
        workflow,
        "## 고급 팁",
        advanced,
        "## 문제 해결",
        troubleshooting,
        "## 사례 기록",
        incidents,
        "## 커뮤니티 관찰",
        community,
        "## 패치 히스토리",
        patches,
        "## 지표 요약",
        metrics,
        "## 참고 자료",
        references,
    ]
    return "\n\n".join(section for section in sections if section.strip())


def ensure_categories() -> None:
    categories = {entry["category"] for entry in BASE_ENTRIES}
    categories.update(page["category"] for page in ANCHOR_PAGES)
    for category in categories:
        WikiCategory.objects.get_or_create(
            name=category,
            defaults={
                "description": f"{category} 관련 문서",
                "color": "#3A7AFE",
                "icon": "fas fa-bookmark",
            },
        )


def ensure_anchor_pages(user: User) -> None:
    now = timezone.now()
    for page in ANCHOR_PAGES:
        WikiPage.objects.get_or_create(
            title=page["title"],
            defaults={
                "summary": page["summary"],
                "category": page["category"],
                "tags": page["tags"],
                "content": page["content"],
                "author": user,
                "is_featured": True,
                "created_at": now,
                "updated_at": now,
            },
        )
    for entry in BASE_ENTRIES:
        content = _anchor_content_from_entry(entry)
        tags = ",".join(filter(None, [entry.get("primary_role", ""), entry["category"], "anchor"]))
        WikiPage.objects.get_or_create(
            title=entry["title"],
            defaults={
                "summary": entry["summary"],
                "category": entry["category"],
                "tags": tags,
                "content": content,
                "author": user,
                "is_featured": True,
                "created_at": now,
                "updated_at": now,
            },
        )


def _bullet(items: Sequence[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else ""


def _paragraphs(items: Sequence[str]) -> str:
    return "\n\n".join(items) if items else ""


def inject_link(content: str, term: str, target: str) -> str:
    if term not in content:
        return content
    patterns = [
        f"[[{term}]]",
        f"[[{target}|{term}]]",
        f"[[{term}|",
    ]
    if any(p in content for p in patterns):
        return content
    link = f"[[{target}|{term}]]" if target != term else f"[[{term}]]"
    return content.replace(term, link, 1)


def cleanup_link_artifacts(content: str) -> tuple[str, bool]:
    cleaned = content.replace("[[[[", "[[").replace("]]]]", "]]")
    return cleaned, cleaned != content


def _merge_metrics(base: Dict[str, str], extra: Dict[str, str]) -> Dict[str, str]:
    merged = dict(base)
    for key, value in extra.items():
        if key not in merged:
            merged[key] = value
    return merged


def _metrics_table(metrics: Dict[str, str]) -> str:
    rows = ["| 지표 | 값 |", "| --- | --- |"]
    for key, value in metrics.items():
        rows.append(f"| {key} | {value} |")
    return "\n".join(rows)


def _reference_section(related: Sequence[str]) -> str:
    lines = []
    for item in related:
        if item.startswith("[[") and item.endswith("]]"):
            lines.append(f"- {item}")
        else:
            lines.append(f"- [[{item}]]")
    return "\n".join(lines)


def build_document(base: Dict[str, object], scenario: Dict[str, object], sequence: int) -> Dict[str, str]:
    title = f"{base['title']} - {scenario['title_suffix']} #{sequence}"
    summary = f"{base['summary']} {scenario['context_hook'].format(name=base['title'])}"

    overview = "\n\n".join(
        [
            scenario["context_hook"].format(name=base["title"]),
            _paragraphs(base.get("background", [])),
        ]
    )
    preparation = _bullet(base.get("preparation", []))
    workflow = _bullet(base.get("workflow", []))
    advanced = "\n\n".join(
        [
            scenario["advanced_summary"],
            _bullet(base.get("advanced", [])),
        ]
    )
    troubleshooting = "\n\n".join(
        [
            scenario["troubleshoot_summary"],
            _bullet(base.get("troubleshooting", [])),
        ]
    )
    incidents = _bullet(base.get("incidents", []))
    community = "\n\n".join(
        [
            scenario["community_context"],
            _bullet(base.get("community", [])),
        ]
    )
    patches = _bullet(base.get("patch_notes", []))
    metrics = _metrics_table(_merge_metrics(base.get("metrics", {}), scenario.get("metrics_extra", {})))
    references = _reference_section(base.get("related", []))

    sections = [
        f"# {title}",
        "## 개요",
        overview,
        "## 준비 사항",
        scenario["strategy_summary"],
        preparation,
        "## 운용 절차",
        _bullet(base.get("workflow", [])),
        "## 고급 전략",
        advanced,
        "## 문제 해결",
        troubleshooting,
        "## 사례 기록",
        incidents,
        "## 커뮤니티 관찰",
        community,
        "## 패치 히스토리",
        patches,
        "## 지표 요약",
        metrics,
        "## 참고 자료",
        references,
    ]

    content = "\n\n".join(section for section in sections if section.strip())
    return {
        "title": title,
        "summary": summary,
        "content": content,
        "category": base["category"],
        "tags": ",".join(
            filter(
                None,
                [
                    base.get("primary_role", ""),
                    base["category"],
                    scenario["focus"],
                ],
            )
        ),
    }


class Command(BaseCommand):
    help = "고품질 위키 문서를 10,000개 이상 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument("--target-count", type=int, default=10000)
        parser.add_argument("--seed", type=int, default=20241026)
        parser.add_argument("--batch-size", type=int, default=64)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="기존 wiki_wikipage 데이터를 전체 삭제 후 다시 채웁니다.",
        )

    def handle(self, *args, **options):
        rng = random.Random(options["seed"])
        target = options["target_count"]
        batch_size = options["batch_size"]

        if options["reset"]:
            WikiPage.objects.all().delete()
            self.stdout.write("기존 위키 데이터를 삭제했습니다.")

        admin = self._ensure_admin()
        ensure_categories()
        ensure_anchor_pages(admin)

        existing_titles = set(WikiPage.objects.values_list("title", flat=True))
        current = len(existing_titles)
        to_generate = max(0, target - current)

        if to_generate == 0:
            self.stdout.write("이미 목표 문서 수를 충족하고 있습니다.")
            return

        self.stdout.write(f"{to_generate}개 문서를 생성합니다.")
        self._generate_documents(admin, to_generate, batch_size, rng, existing_titles)

    def _ensure_admin(self) -> User:
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@stevenwiki.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
        return admin

    def _generate_documents(
        self,
        admin: User,
        to_generate: int,
        batch_size: int,
        rng: random.Random,
        existing_titles: set,
    ) -> None:
        entries = list(BASE_ENTRIES)
        scenarios = list(SCENARIO_VARIANTS)
        combos = len(entries) * len(scenarios)
        repeats = math.ceil(to_generate / combos) if combos else 0

        pages: List[WikiPage] = []
        now = timezone.now()
        seq = 1
        generated = 0

        for repeat in range(max(repeats, 1)):
            rng.shuffle(entries)
            rng.shuffle(scenarios)
            for base in entries:
                for scenario in scenarios:
                    if generated >= to_generate:
                        break
                    document = build_document(base, scenario, seq)
                    seq += 1
                    if document["title"] in existing_titles:
                        continue
                    existing_titles.add(document["title"])
                    cleaned_content, _ = cleanup_link_artifacts(document["content"])
                    page = WikiPage(
                        title=document["title"],
                        summary=document["summary"],
                        content=cleaned_content,
                        category=document["category"],
                        tags=document["tags"],
                        author=admin,
                        created_at=now,
                        updated_at=now,
                        view_count=rng.randint(150, 950),
                        is_featured=False,
                    )
                    pages.append(page)
                    generated += 1

                    if len(pages) >= batch_size:
                        WikiPage.objects.bulk_create(pages, batch_size=batch_size)
                        pages.clear()
                if generated >= to_generate:
                    break
            if generated >= to_generate:
                break

        if pages:
            WikiPage.objects.bulk_create(pages, batch_size=batch_size)
