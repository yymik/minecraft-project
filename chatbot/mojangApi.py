import requests


def get_uuid_info(nickname: str) -> dict:
    """Call Mojang API to resolve the UUID for a given nickname.

    Network access is not always available in this environment, so we catch
    request exceptions and return a structured error instead of raising.
    """
    nickname = (nickname or "").strip()
    if not nickname:
        return {"error": "닉네임을 입력해주세요."}

    url = f"https://api.mojang.com/users/profiles/minecraft/{nickname}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "nickname": data.get("name", nickname),
                "uuid": data.get("id", ""),
            }
        if response.status_code == 204:
            return {"error": "해당 닉네임의 플레이어를 찾을 수 없습니다."}
        return {"error": f"외부 API 오류({response.status_code})"}
    except requests.exceptions.RequestException as exc:
        return {"error": f"UUID 조회에 실패했습니다: {exc}"}
