from django.shortcuts import render, redirect
import json # 세션에 딕셔너리 저장/로드 시 사용 고려 (지금은 ID 리스트만 저장)

# --- 데이터 정의 (예시, 실제로는 더 많은 인챈트 필요) ---
ENCHANTMENTS = {
    "sharpness": {"id": "sharpness", "name": "날카로움 V", "description": "근접 공격력을 크게 증가시킵니다.", "icon": "enchant_icons/sharpness.png", "target_items": ["sword", "axe"]},
    "protection": {"id": "protection", "name": "보호 IV", "description": "대부분의 피해로부터 추가적인 방어력을 제공합니다.", "icon": "enchant_icons/protection.png", "target_items": ["helmet", "chestplate", "leggings", "boots"]},
    "efficiency": {"id": "efficiency", "name": "효율 V", "description": "도구의 채광 및 작업 속도를 크게 증가시킵니다.", "icon": "enchant_icons/efficiency.png", "target_items": ["pickaxe", "axe", "shovel", "hoe", "shears"]},
    "unbreaking": {"id": "unbreaking", "name": "내구성 III", "description": "아이템의 내구도가 감소할 확률을 줄입니다.", "icon": "enchant_icons/unbreaking.png", "target_items": ["all_tools", "all_armor", "weapon", "bow", "fishing_rod", "shield"]}, # 포괄적 아이템 타입
    "mending": {"id": "mending", "name": "수선", "description": "경험치를 얻을 때 내구도를 회복합니다.", "icon": "enchant_icons/mending.png", "target_items": ["all_tools", "all_armor", "weapon", "bow", "fishing_rod", "shield"]},
    "fortune": {"id": "fortune", "name": "행운 III", "description": "특정 블록 파괴 시 드롭 아이템의 양을 늘립니다.", "icon": "enchant_icons/fortune.png", "target_items": ["pickaxe", "axe", "shovel"]},
    "looting": {"id": "looting", "name": "약탈 III", "description": "몹 처치 시 드롭 아이템의 양을 늘립니다.", "icon": "enchant_icons/looting.png", "target_items": ["sword"]},
    "silk_touch": {"id": "silk_touch", "name": "섬세한 손길", "description": "블록을 부술 때 그 블록 자체를 드롭합니다.", "icon": "enchant_icons/silk_touch.png", "target_items": ["pickaxe", "axe", "shovel", "hoe", "shears"]},
    "bane_of_arthropods": {"id": "bane_of_arthropods", "name": "살충 V", "description": "거미, 동굴 거미, 좀벌레, 엔더마이트, 벌에게 추가 피해를 줍니다.", "icon": "enchant_icons/bane_of_arthropods.png", "target_items": ["sword", "axe"]},
    "knockback": {"id": "knockback", "name": "밀치기 II", "description": "공격 시 대상을 더 멀리 밀쳐냅니다.", "icon": "enchant_icons/knockback.png", "target_items": ["sword"]},
    "curse_of_binding": {"id": "curse_of_binding", "name": "귀속 저주", "description": "착용하면 죽기 전까지 벗을 수 없습니다.", "icon": "enchant_icons/curse_of_binding.png", "target_items": ["all_armor", "elytra", "pumpkin", "mob_head"]},
    "curse_of_vanishing": {"id": "curse_of_vanishing", "name": "소실 저주", "description": "죽으면 해당 아이템이 사라집니다.", "icon": "enchant_icons/curse_of_vanishing.png", "target_items": ["all"]},
    # ... (더 많은 인챈트 추가)
}

# 대상 아이템 타입 (예시)
ITEM_TYPES = {
    "sword": "검",
    "pickaxe": "곡괭이",
    "axe": "도끼",
    "shovel": "삽",
    "hoe": "괭이",
    "bow": "활",
    "crossbow": "쇠뇌",
    "fishing_rod": "낚싯대",
    "helmet": "투구",
    "chestplate": "흉갑",
    "leggings": "레깅스",
    "boots": "부츠",
    "shield": "방패",
    "elytra": "겉날개",
    "all_tools": "모든 도구",
    "all_armor": "모든 갑옷",
    "all": "모든 아이템"
}


def recommender_view(request):
    # 세션에서 현재 분류 상태 가져오기 또는 초기화
    # 각 카테고리에는 인챈트 ID 리스트가 저장됨
    recommended_enchants_ids = request.session.get('recommended_enchants_ids', [])
    general_enchants_ids = request.session.get('general_enchants_ids', [])
    not_recommended_enchants_ids = request.session.get('not_recommended_enchants_ids', [])

    # 현재 선택된 장비 아이템 (예: "sword", "pickaxe")
    selected_item_type = request.session.get('selected_item_type', 'sword') # 기본값 검

    message = None

    if request.method == "POST":
        action = request.POST.get("action")
        enchant_id = request.POST.get("enchant_id")
        target_category = request.POST.get("target_category") # "recommended", "general", "not_recommended"
        item_type_from_form = request.POST.get("item_type")

        if action == "select_item_type":
            if item_type_from_form in ITEM_TYPES:
                selected_item_type = item_type_from_form
                # 아이템 타입 변경 시 분류 초기화 (선택사항)
                recommended_enchants_ids = []
                general_enchants_ids = []
                not_recommended_enchants_ids = []
                message = f"'{ITEM_TYPES[selected_item_type]}'에 대한 인챈트 분류를 시작합니다."
            else:
                message = "잘못된 아이템 타입입니다."

        elif action == "move_enchant" and enchant_id in ENCHANTMENTS:
            # 먼저 모든 카테고리에서 해당 인챈트 제거
            if enchant_id in recommended_enchants_ids: recommended_enchants_ids.remove(enchant_id)
            if enchant_id in general_enchants_ids: general_enchants_ids.remove(enchant_id)
            if enchant_id in not_recommended_enchants_ids: not_recommended_enchants_ids.remove(enchant_id)

            # 대상 카테고리에 추가
            if target_category == "recommended":
                recommended_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 추천 인챈트로 이동했습니다."
            elif target_category == "general":
                general_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 일반 인챈트로 이동했습니다."
            elif target_category == "not_recommended":
                not_recommended_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 비추천 인챈트로 이동했습니다."
            elif target_category == "available": # "사용 가능"으로 이동 (즉, 어떤 카테고리에도 속하지 않음)
                 message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 사용 가능한 인챈트 목록으로 되돌렸습니다."
            else:
                message = "잘못된 대상 카테고리입니다."
        
        elif action == "reset_all":
            recommended_enchants_ids = []
            general_enchants_ids = []
            not_recommended_enchants_ids = []
            selected_item_type = 'sword' # 기본값으로 초기화
            message = "모든 분류를 초기화했습니다."


        # 세션에 변경된 상태 저장
        request.session['recommended_enchants_ids'] = recommended_enchants_ids
        request.session['general_enchants_ids'] = general_enchants_ids
        request.session['not_recommended_enchants_ids'] = not_recommended_enchants_ids
        request.session['selected_item_type'] = selected_item_type
        
        return redirect('enchant_recommender:recommender') # POST 후 Redirect (PRG 패턴)

    # 현재 선택된 아이템 타입에 적용 가능한 인챈트 필터링
    # "all", "all_tools", "all_armor" 등 포괄적인 타입 고려
    available_enchants = {}
    classified_ids = set(recommended_enchants_ids + general_enchants_ids + not_recommended_enchants_ids)

    for eid, edata in ENCHANTMENTS.items():
        if eid not in classified_ids: # 아직 분류되지 않은 인챈트 중에서
            # 인챈트의 target_items 와 현재 selected_item_type 비교
            can_apply = False
            for target in edata["target_items"]:
                if target == selected_item_type or \
                   target == "all" or \
                   (target == "all_tools" and selected_item_type in ["pickaxe", "axe", "shovel", "hoe", "shears"]) or \
                   (target == "all_armor" and selected_item_type in ["helmet", "chestplate", "leggings", "boots"]) or \
                   (target == "weapon" and selected_item_type in ["sword", "axe", "bow", "crossbow"]): # "weapon"도 고려
                    can_apply = True
                    break
            if can_apply:
                available_enchants[eid] = edata


    context = {
        'item_types': ITEM_TYPES,
        'selected_item_type': selected_item_type,
        'selected_item_name': ITEM_TYPES.get(selected_item_type, "알 수 없는 아이템"),
        'all_enchants_data': ENCHANTMENTS, # 템플릿에서 ID로 정보 참조 시 필요
        'available_enchants': available_enchants, # 아직 분류 안 된, 현재 아이템에 적용 가능한 인챈트
        'recommended_enchants_ids': recommended_enchants_ids,
        'general_enchants_ids': general_enchants_ids,
        'not_recommended_enchants_ids': not_recommended_enchants_ids,
        'message': request.session.pop('message', message) # POST 후 redirect 시 메시지 전달, 없으면 현재 메시지
    }
    # POST 후 redirect시 message가 있다면 세션에서 가져오고 삭제, 없다면 현재 message 사용
    if request.method == "GET" and 'message' in request.session: # GET이고 세션에 메시지가 있으면
        context['message'] = request.session.pop('message')

    return render(request, "enchant_recommender/recommender.html", context)