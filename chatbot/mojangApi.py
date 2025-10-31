import base64
import json
from typing import Dict, Optional

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


def get_skin_profile(uuid: str) -> Dict[str, Optional[str]]:
    """Fetch raw skin texture URL and ready-to-use renders for a given UUID."""
    uuid = (uuid or "").strip()
    if not uuid:
        return {"error": "UUID가 필요합니다."}

    profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    try:
        response = requests.get(profile_url, timeout=5)
        if response.status_code != 200:
            return {"error": f"스킨 정보를 불러오지 못했습니다({response.status_code})."}

        data = response.json()
        properties = data.get("properties") or []
        textures = next((prop for prop in properties if prop.get("name") == "textures"), None)
        if not textures:
            return {"error": "스킨 텍스처 정보가 없습니다."}

        decoded = base64.b64decode(textures.get("value", "")).decode("utf-8")
        texture_json = json.loads(decoded)
        skin_url = (
            texture_json.get("textures", {})
            .get("SKIN", {})
            .get("url")
        )
        if not skin_url:
            return {"error": "스킨 URL을 찾지 못했습니다."}

        render_base = f"https://crafatar.com/renders/body/{uuid}?overlay"
        avatar_base = f"https://crafatar.com/avatars/{uuid}?overlay"

        return {
            "skin_url": skin_url,
            "render_url": render_base,
            "avatar_url": avatar_base,
        }
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError, base64.binascii.Error) as exc:
        return {"error": f"스킨 정보를 불러오지 못했습니다: {exc}"}
