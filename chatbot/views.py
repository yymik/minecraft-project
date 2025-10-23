from copy import deepcopy

from django.shortcuts import render
from django.utils import timezone
from .dialogflow import get_dialogflow_response
from .mojangApi import get_uuid_info


# 샘플 플레이어 데이터 (네트워크 불가 환경 대비)
SAMPLE_PLAYERS = {
    "steve": {
        "nickname": "Steve",
        "uuid": "8667ba71b85a4004af54457a9734eed7",
        "skin_url": "https://static.wikia.nocookie.net/minecraft_gamepedia/images/2/20/Steve_Render.png",
        "last_seen": "2025-01-10",
        "notes": "기본 남성 캐릭터 스킨",
    },
    "alex": {
        "nickname": "Alex",
        "uuid": "ec561538f3fd461daff5086b22154bce",
        "skin_url": "https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/bd/Alex_render.png",
        "last_seen": "2025-01-11",
        "notes": "기본 여성 캐릭터 스킨",
    },
    "notch": {
        "nickname": "Notch",
        "uuid": "069a79f444e94726a5befca90e38aaf5",
        "skin_url": "https://static.wikia.nocookie.net/minecraft_gamepedia/images/1/18/Markus_Persson.png",
        "last_seen": "2024-12-25",
        "notes": "마인크래프트 창시자",
    },
}


def chat_view(request):
    # Initialize session history
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    chat_history = request.session['chat_history']
    uuid_info = None

    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        if user_input:
            # Append user message
            chat_history.append({"role": "user", "text": user_input})

            # UUID helper
            if user_input.lower().startswith("uuid "):
                nickname = user_input.split(" ", 1)[1]
                uuid_info = get_uuid_info(nickname)

            # Bot response
            bot_text = get_dialogflow_response(user_input)
            chat_history.append({"role": "bot", "text": bot_text})

            # Persist session
            request.session['chat_history'] = chat_history
            request.session.modified = True

    return render(request, "chatbot/chat.html", {
        "chat_history": chat_history,
        "uuid_info": uuid_info,
    })


def user_info_view(request):
    query = ""
    result = None
    error = None
    recent_searches = request.session.get("mc_recent_searches", [])

    if request.method == "POST":
        query = (request.POST.get("nickname") or "").strip()
        if not query:
            error = "닉네임을 입력해주세요."
        else:
            lookup = get_uuid_info(query)
            if lookup and not lookup.get("error") and lookup.get("uuid"):
                result = {
                    "nickname": lookup.get("nickname", query),
                    "uuid": lookup.get("uuid"),
                    "source": "모장 공식 API",
                    "skin_url": None,
                    "last_seen": timezone.now().date().isoformat(),
                    "notes": "외부 API에서 조회한 결과입니다.",
                }
            else:
                sample = SAMPLE_PLAYERS.get(query.lower())
                if sample:
                    result = deepcopy(sample)
                    result["source"] = "샘플 데이터"
                else:
                    error = lookup.get("error") if lookup else "플레이어 정보를 찾을 수 없습니다."

        if result:
            history = [query] + [item for item in recent_searches if item.lower() != query.lower()]
            request.session["mc_recent_searches"] = history[:5]
            request.session.modified = True
            recent_searches = history[:5]

    context = {
        "query": query,
        "result": result,
        "error": error,
        "recent_searches": recent_searches,
        "sample_players": [data for data in SAMPLE_PLAYERS.values()],
    }
    return render(request, "chatbot/user_info.html", context)
