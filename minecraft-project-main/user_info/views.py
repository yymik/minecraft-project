import requests
from django.shortcuts import render

def user_info_view(request):
    context = {}

    if request.method == "POST":
        username = request.POST.get("username")

        if username:
            # 닉네임 -> UUID
            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                uuid = data.get("id")
                context["uuid"] = uuid
                context["username"] = data.get("name")

                # 닉네임 변경 기록 가져오기
                names_url = f"https://api.mojang.com/user/profiles/{uuid}/names"
                names_res = requests.get(names_url)
                if names_res.status_code == 200:
                    context["name_history"] = names_res.json()

                # 스킨/프로필 정보 가져오기
                profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}?unsigned=false"
                profile_res = requests.get(profile_url)
                if profile_res.status_code == 200:
                    profile_data = profile_res.json()
                    context["profile"] = profile_data

            elif response.status_code == 204:
                context["error"] = "존재하지 않는 닉네임입니다."
            else:
                context["error"] = f"API 요청 실패 (status {response.status_code})"

    return render(request, "user_info/user_info.html", context)
