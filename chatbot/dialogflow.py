"""
Dialogflow integration with graceful fallbacks for offline environments.
"""

import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional

from django.conf import settings
from google.api_core import exceptions as google_exceptions
from google.cloud import dialogflow_v2 as dialogflow
from wiki.models import WikiPage

logger = logging.getLogger(__name__)

_session_client: Optional[dialogflow.SessionsClient] = None


@lru_cache(maxsize=1)
def _load_config():
    defaults = {
        "ENABLED": False,
        "PROJECT_ID": "",
        "LANGUAGE_CODE": "ko",
        "SESSION_PREFIX": "mcwiki",
    }
    raw = getattr(settings, "DIALOGFLOW", {}) or {}
    defaults.update(raw)
    return defaults


def dialogflow_enabled() -> bool:
    cfg = _load_config()
    return bool(cfg.get("ENABLED")) and bool(cfg.get("PROJECT_ID"))


def _get_session_client() -> dialogflow.SessionsClient:
    global _session_client
    if _session_client is None:
        _session_client = dialogflow.SessionsClient()
    return _session_client


def detect_intent(text: str, session_id: str = "anonymous") -> Optional[str]:
    cfg = _load_config()
    if not dialogflow_enabled():
        return None

    try:
        client = _get_session_client()
        session_path = client.session_path(
            cfg["PROJECT_ID"],
            f"{cfg.get('SESSION_PREFIX', 'mcwiki')}-{session_id}",
        )
        text_input = dialogflow.TextInput(text=text, language_code=cfg.get("LANGUAGE_CODE", "ko"))
        query_input = dialogflow.QueryInput(text=text_input)
        response = client.detect_intent(request={"session": session_path, "query_input": query_input})
        fulfillment = response.query_result.fulfillment_text
        return fulfillment or None
    except google_exceptions.GoogleAPICallError as exc:
        logger.error("Dialogflow API error: %s", exc)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Dialogflow unexpected error: %s", exc)
    return None


def get_dialogflow_response(user_input: str, session_id: str = "anonymous") -> str:
    text = (user_input or "").strip()
    if not text:
        return "질문을 입력해주세요."

    if text.lower().startswith("uuid "):
        return "닉네임의 UUID 정보를 조회합니다..."

    if dialogflow_enabled():
        result = detect_intent(text, session_id=session_id)
        if result:
            return result

    return fallback_response(text)


def fallback_response(text: str) -> str:
    lower = text.lower()

    if any(greet in lower for greet in ["안녕", "hello", "hi"]):
        return "안녕하세요! 마인크래프트 관련 질문이 있으시면 언제든 물어보세요!"

    if "시간" in text or "몇시" in text:
        return f"지금 시간은 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 입니다."

    wiki_answer = search_wiki_content(text)
    if wiki_answer:
        return wiki_answer

    minecraft_answer = get_minecraft_responses(text)
    if minecraft_answer:
        return minecraft_answer

    return "질문을 이해하지 못했어요. 마인크래프트 관련 질문을 해보시거나 다른 표현으로 질문해 주세요."


def search_wiki_content(query: str) -> Optional[str]:
    try:
        pages = WikiPage.objects.filter(title__icontains=query)[:3]
        if not pages:
            pages = WikiPage.objects.filter(content__icontains=query)[:3]
        if not pages:
            pages = WikiPage.objects.filter(tags__icontains=query)[:3]

        if pages:
            response_lines = [f"'{query}'에 대한 정보를 찾았습니다:\n"]
            for page in pages:
                summary = page.summary or f"{page.content[:100]}..."
                response_lines.append(f"📖 **{page.title}**\n{summary}\n🔗 자세히 보기: /wiki/{page.title}/\n")
            return "\n".join(response_lines)
    except Exception as exc:  # pragma: no cover - defensive log
        logger.warning("Wiki search failed: %s", exc)

    return None


def get_minecraft_responses(text: str) -> Optional[str]:
    lower = text.lower()

    if any(ore in lower for ore in ["다이아몬드", "다이아", "diamond"]):
        return (
            "💎 **다이아몬드**에 대해 알려드릴게요!\n\n"
            "다이아몬드는 마인크래프트에서 가장 귀중한 광물 중 하나입니다.\n\n"
            "📍 **획득 방법:**\n"
            "- Y좌표 16 이하에서 발견\n"
            "- 철 곡괭이 이상 필요\n"
            "- 생성 확률: 매우 낮음 (0.1%)\n\n"
            "🔧 **용도:**\n"
            "- 다이아몬드 도구 제작\n"
            "- 다이아몬드 갑옷 제작\n"
            "- 인챈트 테이블 제작\n\n"
            "📖 자세한 정보: /wiki/다이아몬드/"
        )

    if any(ore in lower for ore in ["철", "iron"]):
        return (
            "⛏️ **철 광석**에 대해 알려드릴게요!\n\n"
            "철 광석은 마인크래프트에서 가장 유용한 광물 중 하나입니다.\n\n"
            "📍 **획득 방법:**\n"
            "- Y좌표 64 이하에서 발견\n"
            "- 돌 곡괭이 이상 필요\n"
            "- 생성 확률: 높음 (1.3%)\n\n"
            "🔧 **용도:**\n"
            "- 철괴 제작 (제련 필요)\n"
            "- 철 도구 및 갑옷 제작\n"
            "- 레일 제작\n\n"
            "📖 자세한 정보: /wiki/철 광석/"
        )

    if any(ore in lower for ore in ["청금석", "lapis", "청금"]):
        return (
            "💙 **청금석**에 대해 알려드릴게요!\n\n"
            "청금석은 마인크래프트에서 인챈트에 사용되는 중요한 광물입니다.\n\n"
            "📍 **획득 방법:**\n"
            "- Y좌표 64 이하의 동굴에서 발견\n"
            "- 돌 곡괭이 이상 필요\n"
            "- 광맥당 4-8개 생성\n\n"
            "🔧 **용도:**\n"
            "- 인챈트 테이블에서 인챈트 레벨 소모\n"
            "- 청금석 블록 제작\n"
            "- 파란색 염료 제작\n\n"
            "📖 자세한 정보: /wiki/청금석/"
        )

    if any(ench in lower for ench in ["인챈트", "enchant"]):
        return (
            "✨ **인챈트**에 대해 알려드릴게요!\n\n"
            "인챈트는 마인크래프트에서 도구와 갑옷에 특별한 능력을 부여하는 시스템입니다.\n\n"
            "🔮 **인챈트 테이블:**\n"
            "- 책 1개 + 다이아몬드 2개 + 흑요석 4개로 제작\n"
            "- 최대 30레벨까지 사용 가능\n"
            "- 청금석으로 레벨 소모\n\n"
            "⚔️ **주요 인챈트:**\n"
            "- 효율성: 채굴 속도 증가\n"
            "- 날카로움: 공격력 증가\n"
            "- 보호: 모든 피해 감소\n\n"
            "📖 자세한 정보: /wiki/인챈트/"
        )

    if any(brew in lower for brew in ["양조", "포션", "potion"]):
        return (
            "🧪 **양조**에 대해 알려드릴게요!\n\n"
            "양조는 마인크래프트에서 물약을 제작하는 시스템입니다.\n\n"
            "⚗️ **양조기:**\n"
            "- 화염 가루 + 막대기 3개로 제작\n"
            "- 네더 사마귀 + 물병으로 거친 물약 제작\n\n"
            "💊 **주요 물약:**\n"
            "- 힘: 블레이즈 가루 + 거친 물약\n"
            "- 신속: 설탕 + 거친 물약\n"
            "- 점프: 토끼의 발 + 거친 물약\n\n"
            "📖 자세한 정보: /wiki/양조/"
        )

    if any(mob in lower for mob in ["크리퍼", "creeper"]):
        return (
            "💥 **크리퍼**에 대해 알려드릴게요!\n\n"
            "크리퍼는 마인크래프트의 대표적인 적대적 몹입니다.\n\n"
            "⚠️ **특징:**\n"
            "- 플레이어 근처에서 폭발\n"
            "- '쉿' 소리로 경고\n"
            "- 폭발로 블록 파괴 및 피해\n\n"
            "🎯 **대처법:**\n"
            "- 3블록 이상 거리 유지\n"
            "- 활로 원거리 공격\n"
            "- 빠르게 도망가기\n\n"
            "📖 자세한 정보: /wiki/크리퍼/"
        )

    if any(tool in lower for tool in ["도구", "tool", "곡괭이", "pickaxe"]):
        return (
            "🛠️ **도구**에 대해 알려드릴게요!\n\n"
            "마인크래프트에는 다양한 도구들이 있습니다.\n\n"
            "⛏️ **곡괭이:**\n"
            "- 나무: 59회 사용\n"
            "- 돌: 131회 사용\n"
            "- 철: 250회 사용\n"
            "- 다이아몬드: 1,561회 사용\n\n"
            "⚔️ **검:**\n"
            "- 나무: 59회 사용\n"
            "- 돌: 131회 사용\n"
            "- 철: 250회 사용\n"
            "- 다이아몬드: 1,561회 사용\n\n"
            "📖 자세한 정보: /wiki/도구/"
        )

    return None
