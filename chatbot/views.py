from django.shortcuts import render
from .dialogflow import get_dialogflow_response
from .mojangApi import get_uuid_info

def chat_view(request):
    user_input = None
    bot_response = None
    uuid_info = None

    if request.method == "POST":
        user_input = request.POST.get("user_input", "")
        bot_response = get_dialogflow_response(user_input)

        # 예: "uuid 닉네임" 입력 시 UUID 처리
        if user_input.lower().startswith("uuid "):
            nickname = user_input.split(" ", 1)[1]
            uuid_info = get_uuid_info(nickname)

    return render(request, "chatbot/chat.html", {
        "user_input": user_input,
        "bot_response": bot_response,
        "uuid_info": uuid_info
    })

