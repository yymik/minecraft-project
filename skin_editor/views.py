# skin_editor/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
import requests
import base64
import json # Mojang API 응답의 texture 값을 파싱하기 위함

def editor_page_view(request):
    """스킨 편집기 HTML 페이지를 렌더링합니다."""
    return render(request, 'skin_editor/editor.html')

def get_skin_api_view(request):
    """
    Mojang API를 통해 플레이어 스킨 정보를 가져와 프론트엔드에 전달합니다.
    CORS 문제를 우회하기 위한 백엔드 프록시 역할을 합니다.
    """
    username = request.GET.get('username')
    if not username:
        return HttpResponseBadRequest(json.dumps({'error': "Username parameter is required."}), content_type="application/json")

    skin_png_url = None
    error_message = None

    try:
        # 1단계: 사용자 이름으로 UUID 조회 (Mojang API)
        uuid_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        uuid_response = requests.get(uuid_url, timeout=5) # 타임아웃 설정
        uuid_response.raise_for_status() # 200 OK가 아니면 예외 발생
        uuid_data = uuid_response.json()
        uuid = uuid_data.get('id')

        if not uuid:
            error_message = f"플레이어 '{username}'의 UUID를 찾을 수 없습니다."
        else:
            # 2단계: UUID로 스킨 정보 조회 (Mojang API - 세션 서버)
            profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
            profile_response = requests.get(profile_url, timeout=5)
            profile_response.raise_for_status()
            profile_data = profile_response.json()

            if profile_data.get('properties'):
                textures_property = next(
                    (prop for prop in profile_data['properties'] if prop['name'] == 'textures'),
                    None
                )
                if textures_property:
                    # Base64 디코딩 후 JSON 파싱
                    texture_value_decoded = base64.b64decode(textures_property['value']).decode('utf-8')
                    texture_json_data = json.loads(texture_value_decoded)

                    if texture_json_data.get('textures', {}).get('SKIN', {}).get('url'):
                        skin_png_url = texture_json_data['textures']['SKIN']['url']
                    else:
                        error_message = f"플레이어 '{username}'의 스킨 텍스처 URL을 찾을 수 없습니다."
                else:
                    error_message = f"플레이어 '{username}'의 텍스처 정보를 찾을 수 없습니다."
            else:
                error_message = f"플레이어 '{username}'의 프로필 속성을 찾을 수 없습니다."

    except requests.exceptions.Timeout:
        error_message = "Mojang API 요청 시간 초과."
    except requests.exceptions.RequestException as e:
        error_message = f"Mojang API 요청 중 오류 발생: {e}"
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as e:
        error_message = f"API 응답 처리 중 오류 발생: {e}"


    if skin_png_url:
        return JsonResponse({'skin_url': skin_png_url})
    else:
        return JsonResponse({'error': error_message or "알 수 없는 오류로 스킨을 불러오지 못했습니다."}, status=404)