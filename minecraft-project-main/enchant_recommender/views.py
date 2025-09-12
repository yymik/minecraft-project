from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]
posts_collection = db["enchant_posts"]
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

def enchant_main_view(request):
    posts = []
    for post in posts_collection.find():
        post["id"] = str(post["_id"])  # 새 필드로 변환
        posts.append(post)
    return render(request, "enchant_recommender/enchant_main.html", {"posts": posts})

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

def like_post(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        if post_id:
            post = posts_collection.find_one({"_id": ObjectId(post_id)})
            if post:
                # 좋아요 수 증가 (없으면 0에서 시작)
                new_likes = post.get("likes", 0) + 1
                posts_collection.update_one(
                    {"_id": ObjectId(post_id)},
                    {"$set": {"likes": new_likes}}
                )
        return redirect("enchant_recommender:main")

from django.shortcuts import render, redirect
from bson import ObjectId

def recommender_view(request):
    # --- 1. URL에서 post_id로 불러오기 ---
    post_id = request.GET.get("post_id")
    if post_id:
        try:
            post = posts_collection.find_one({"_id": ObjectId(post_id)})
        except Exception:
            post = None

        if post:
            # 게시물 내용에서 인챈트 추출
            content = post.get("content", "")
            selected_item_type = "sword"  # TODO: 게시물 저장할 때 item_type을 따로 저장해두면 더 정확함
            recommended_enchants_ids = []

            for eid, edata in ENCHANTMENTS.items():
                if edata["name"] in content:
                    recommended_enchants_ids.append(eid)

            # 세션 초기화 후 반영
            request.session['recommended_enchants_ids'] = recommended_enchants_ids
            request.session['general_enchants_ids'] = []
            request.session['not_recommended_enchants_ids'] = []
            request.session['selected_item_type'] = selected_item_type

            return redirect("enchant_recommender:recommender")

    # --- 2. 세션에서 현재 상태 가져오기 ---
    recommended_enchants_ids = request.session.get('recommended_enchants_ids', [])
    general_enchants_ids = request.session.get('general_enchants_ids', [])
    not_recommended_enchants_ids = request.session.get('not_recommended_enchants_ids', [])
    selected_item_type = request.session.get('selected_item_type', 'sword')

    message = None

    # --- 3. POST 요청 처리 ---
    if request.method == "POST":
        action = request.POST.get("action")
        enchant_id = request.POST.get("enchant_id")
        target_category = request.POST.get("target_category")
        item_type_from_form = request.POST.get("item_type")

        if action == "select_item_type":
            if item_type_from_form in ITEM_TYPES:
                selected_item_type = item_type_from_form
                # 아이템 타입 바꾸면 초기화
                recommended_enchants_ids = []
                general_enchants_ids = []
                not_recommended_enchants_ids = []
                message = f"'{ITEM_TYPES[selected_item_type]}'에 대한 인챈트 분류를 시작합니다."
            else:
                message = "잘못된 아이템 타입입니다."

        elif action == "move_enchant" and enchant_id in ENCHANTMENTS:
            # 모든 카테고리에서 제거
            for lst in [recommended_enchants_ids, general_enchants_ids, not_recommended_enchants_ids]:
                if enchant_id in lst:
                    lst.remove(enchant_id)

            # 지정한 카테고리에 추가
            if target_category == "recommended":
                recommended_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 추천 인챈트로 이동했습니다."
            elif target_category == "general":
                general_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 일반 인챈트로 이동했습니다."
            elif target_category == "not_recommended":
                not_recommended_enchants_ids.append(enchant_id)
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 비추천 인챈트로 이동했습니다."
            elif target_category == "available":
                message = f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 목록으로 되돌렸습니다."
            else:
                message = "잘못된 대상 카테고리입니다."

        elif action == "reset_all":
            recommended_enchants_ids = []
            general_enchants_ids = []
            not_recommended_enchants_ids = []
            selected_item_type = 'sword'
            message = "모든 분류를 초기화했습니다."

        elif action == "save_post":
            title = request.POST.get("title", "새 인챈트 빌드")
            content = f"{ITEM_TYPES[selected_item_type]} 추천 인챈트: " \
                      f"{', '.join([ENCHANTMENTS[e]['name'] for e in recommended_enchants_ids])}"

            posts_collection.insert_one({
                "title": title,
                "content": content,
                "item_type": selected_item_type
            })
            return redirect("enchant_recommender:main")

        # 세션 업데이트
        request.session['recommended_enchants_ids'] = recommended_enchants_ids
        request.session['general_enchants_ids'] = general_enchants_ids
        request.session['not_recommended_enchants_ids'] = not_recommended_enchants_ids
        request.session['selected_item_type'] = selected_item_type

        return redirect("enchant_recommender:recommender")

    # --- 4. 적용 가능한 인챈트 필터링 ---
    available_enchants = {}
    classified_ids = set(recommended_enchants_ids + general_enchants_ids + not_recommended_enchants_ids)

    for eid, edata in ENCHANTMENTS.items():
        if eid not in classified_ids:
            can_apply = False
            for target in edata["target_items"]:
                if (
                    target == selected_item_type
                    or target == "all"
                    or (target == "all_tools" and selected_item_type in ["pickaxe", "axe", "shovel", "hoe", "shears"])
                    or (target == "all_armor" and selected_item_type in ["helmet", "chestplate", "leggings", "boots"])
                    or (target == "weapon" and selected_item_type in ["sword", "axe", "bow", "crossbow"])
                ):
                    can_apply = True
                    break
            if can_apply:
                available_enchants[eid] = edata

    # --- 5. 컨텍스트 구성 ---
    context = {
        "item_types": ITEM_TYPES,
        "selected_item_type": selected_item_type,
        "selected_item_name": ITEM_TYPES.get(selected_item_type, "알 수 없는 아이템"),
        "all_enchants_data": ENCHANTMENTS,
        "available_enchants": available_enchants,
        "recommended_enchants_ids": recommended_enchants_ids,
        "general_enchants_ids": general_enchants_ids,
        "not_recommended_enchants_ids": not_recommended_enchants_ids,
        "message": request.session.pop("message", message),
    }

    return render(request, "enchant_recommender/recommender.html", context)
