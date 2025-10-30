from django.shortcuts import render, redirect, get_object_or_404 # 필요한 함수 모두 임포트
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
# from bson import ObjectId # 제거
from .models import EnchantmentRecommendation, Like # 👈 Like 모델 임포트
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F # 업데이트 시 데이터 경합 방지용 import
from .models import EnchantmentRecommendation, Like # 👈 Like 모델 임포트
from bson import ObjectId # recommender_view 위에 남아있는 불필요한 임포트도 제거해야 합니다.

#client = MongoClient("mongodb://localhost:27017")
#b = client["minecraft"]
#posts_collection = db["enchant_posts"]
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
# --- 헬퍼 함수 ---
def get_applicable_enchants(selected_item_type, exclude_enchants_ids=None):
    if exclude_enchants_ids is None:
        exclude_enchants_ids = []

    applicable = {}
    for eid, edata in ENCHANTMENTS.items():
        if eid in exclude_enchants_ids:
            continue
        can_apply = False
        for target in edata["target_items"]:
            if target == selected_item_type or \
               target == "all" or \
               (target == "all_tools" and selected_item_type in ["pickaxe", "axe", "shovel", "hoe", "shears"]) or \
               (target == "all_armor" and selected_item_type in ["helmet", "chestplate", "leggings", "boots"]) or \
               (target == "weapon" and selected_item_type in ["sword", "axe", "bow", "crossbow"]):
                can_apply = True
                break
        if can_apply:
            applicable[eid] = edata
    return applicable

def enchant_main_view(request):
    # RDB 모델 사용: 모든 추천 게시물 가져오기
    posts = EnchantmentRecommendation.objects.all().order_by('-created_at')

    # 로그인한 사용자라면, 좋아요 누른 게시물 PK 목록 가져오기
    liked_post_pks = []
    if request.user.is_authenticated:
        # 쿼리셋을 사용하여 좋아요 누른 게시물의 PK만 리스트로 가져옴
        liked_post_pks = Like.objects.filter(user=request.user).values_list('recommendation__pk', flat=True)

    context = {
        "posts": posts,
        "liked_post_pks": list(liked_post_pks), # 템플릿에서 사용하기 위해 리스트로 변환
        "item_types": ITEM_TYPES,
    }
    return render(request, "enchant_recommender/enchant_main.html", context)
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
# 3. 인챈트 적용 가능 여부를 판단하는 헬퍼 함수 (재사용성을 위해 분리)
def get_applicable_enchants(selected_item_type, exclude_enchants_ids=None):
    if exclude_enchants_ids is None:
        exclude_enchants_ids = []

    applicable = {}
    for eid, edata in ENCHANTMENTS.items():
        if eid in exclude_enchants_ids:
            continue

        can_apply = False
        for target in edata["target_items"]:
            if target == selected_item_type or \
               target == "all" or \
               (target == "all_tools" and selected_item_type in ["pickaxe", "axe", "shovel", "hoe", "shears"]) or \
               (target == "all_armor" and selected_item_type in ["helmet", "chestplate", "leggings", "boots"]) or \
               (target == "weapon" and selected_item_type in ["sword", "axe", "bow", "crossbow"]):
                can_apply = True
                break
        if can_apply:
            applicable[eid] = edata
    return applicable


@login_required
def like_post(request):
    # 좋아요 로직은 완벽하게 RDB/SQLite 기반입니다.
    if request.method == "POST":
        post_pk = request.POST.get("post_pk")

        if not post_pk:
            messages.error(request, "잘못된 접근입니다.")
            return redirect("enchant_recommender:main")

        recommendation = get_object_or_404(EnchantmentRecommendation, pk=post_pk)

        # 계정당 하나만 가능하도록, Like 모델을 통해 좋아요 여부 확인
        is_liked = Like.objects.filter(user=request.user, recommendation=recommendation).exists()

        if is_liked:
            # 좋아요 취소
            Like.objects.filter(user=request.user, recommendation=recommendation).delete()
            recommendation.likes_count = F('likes_count') - 1
            recommendation.save()
            messages.info(request, "좋아요를 취소했습니다.")
        else:
            # 좋아요
            try:
                Like.objects.create(user=request.user, recommendation=recommendation)
                recommendation.likes_count = F('likes_count') + 1
                recommendation.save()
                messages.success(request, "이 추천에 좋아요를 눌렀습니다!")
            except:
                messages.error(request, "좋아요 처리 중 오류가 발생했습니다.")

        recommendation.refresh_from_db()

        return redirect("enchant_recommender:main")

    return redirect("enchant_recommender:main")

from django.shortcuts import render, redirect
from bson import ObjectId


def start_new_recommendation_view(request):
    # 'accounts:forgot'로 URL이 지정되어 있지만, 여기서는 'home'으로 가정합니다.
    # 만약 'enchant_recommender:main'으로 돌아가려면 redirect('enchant_recommender:main')을 사용합니다.

    # 세션 데이터 초기화
    if 'recommended_enchants_ids' in request.session:
        del request.session['recommended_enchants_ids']
    if 'general_enchants_ids' in request.session:
        del request.session['general_enchants_ids']
    if 'not_recommended_enchants_ids' in request.session:
        del request.session['not_recommended_enchants_ids']
    if 'selected_item_type' in request.session:
        del request.session['selected_item_type']

    # 제목/메모 임시 저장 데이터도 삭제
    if 'temp_title' in request.session:
        del request.session['temp_title']
    if 'temp_memo' in request.session:
        del request.session['temp_memo']

    # 새로운 추천기 페이지로 리다이렉트 (새로운 세션으로 시작)
    return redirect('enchant_recommender:recommender')


def recommender_view(request):
    # GET 요청 시 초기화되거나 이전 값 불러오기
    recommended_enchants_ids = request.session.get('recommended_enchants_ids', [])
    general_enchants_ids = request.session.get('general_enchants_ids', [])
    not_recommended_enchants_ids = request.session.get('not_recommended_enchants_ids', [])
    selected_item_type = request.session.get('selected_item_type', 'sword')

    # 💡 제목/메모 유지: 세션에서 임시 저장된 값 가져오기 (가져온 후 세션에서 삭제)
    temp_title = request.session.pop('temp_title', '')
    temp_memo = request.session.pop('temp_memo', '')

    # messages 프레임워크 사용 (message 변수는 context에 포함되지 않음)

    if request.method == "POST":
        action = request.POST.get("action")
        # 💡 POST에서 제목과 메모 내용을 항상 먼저 가져옴
        title_content = request.POST.get("title_content", "").strip()
        memo_content = request.POST.get("memo_content", "").strip()

        if action == "select_item_type":
            if item_type_from_form := request.POST.get("item_type"):
                if item_type_from_form in ITEM_TYPES:
                    selected_item_type = item_type_from_form
                    # 아이템 타입 변경 시 분류 초기화
                    recommended_enchants_ids = []
                    general_enchants_ids = []
                    not_recommended_enchants_ids = []
                    messages.info(request, f"'{ITEM_TYPES[selected_item_type]}'에 대한 인챈트 분류를 시작합니다.")
                else:
                    messages.error(request, "잘못된 아이템 타입입니다.")

        elif action == "move_enchant":
            enchant_id = request.POST.get("enchant_id")
            target_category = request.POST.get("target_category")

            if enchant_id in ENCHANTMENTS:
                # 먼저 모든 카테고리에서 해당 인챈트 제거
                if enchant_id in recommended_enchants_ids: recommended_enchants_ids.remove(enchant_id)
                if enchant_id in general_enchants_ids: general_enchants_ids.remove(enchant_id)
                if enchant_id in not_recommended_enchants_ids: not_recommended_enchants_ids.remove(enchant_id)

                # 대상 카테고리에 추가
                if target_category == "recommended":
                    recommended_enchants_ids.append(enchant_id)
                    messages.info(request, f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 추천 인챈트로 이동했습니다.")
                elif target_category == "general":
                    general_enchants_ids.append(enchant_id)
                    messages.info(request, f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 일반 인챈트로 이동했습니다.")
                elif target_category == "not_recommended":
                    not_recommended_enchants_ids.append(enchant_id)
                    messages.info(request, f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 비추천 인챈트로 이동했습니다.")
                elif target_category == "available":  # 사용 가능 목록으로 되돌림
                    messages.info(request, f"'{ENCHANTMENTS[enchant_id]['name']}'을(를) 사용 가능한 인챈트 목록으로 되돌렸습니다.")
                else:
                    messages.error(request, "잘못된 대상 카테고리입니다.")
            else:
                messages.error(request, "존재하지 않는 인챈트입니다.")

        # 💡 분류/이동/선택 시: 제목과 메모를 세션에 임시 저장 (페이지 이동 후 값 유지)
        if action in ["move_enchant", "select_item_type"]:
            request.session['temp_title'] = title_content
            request.session['temp_memo'] = memo_content

        elif action == "reset_all":
            # reset_all은 start_new_recommendation_view에서 처리하도록 URL을 변경했으나,
            # 폼이 action=reset_all을 보낼 수도 있으므로 기존 로직 유지 (분류만 초기화)
            recommended_enchants_ids = []
            general_enchants_ids = []
            not_recommended_enchants_ids = []
            selected_item_type = 'sword'
            messages.info(request, "모든 분류를 초기화했습니다.")
            # 임시 저장된 제목/메모도 삭제
            if 'temp_title' in request.session: del request.session['temp_title']
            if 'temp_memo' in request.session: del request.session['temp_memo']


        elif action == "save_recommendation":
            if not request.user.is_authenticated:
                messages.error(request, "로그인 후 저장할 수 있습니다.")
                request.session['temp_title'] = title_content
                request.session['temp_memo'] = memo_content
                return redirect('accounts:login')

            if not title_content:
                messages.error(request, "제목을 입력해주세요.")
                request.session['temp_memo'] = memo_content  # 메모만 유지
                return redirect('enchant_recommender:recommender')  # 제목은 required이므로 입력 요청

            if not (recommended_enchants_ids or general_enchants_ids or not_recommended_enchants_ids):
                messages.warning(request, "아직 분류된 인챈트가 없습니다. 먼저 인챈트를 분류해주세요.")
                # 저장 실패 시 제목/메모 세션에 다시 저장
                request.session['temp_title'] = title_content
                request.session['temp_memo'] = memo_content
                return redirect('enchant_recommender:recommender')
            else:
                # DB 저장
                EnchantmentRecommendation.objects.create(
                    user=request.user,
                    item_type=selected_item_type,
                    title=title_content,
                    recommended_enchants=recommended_enchants_ids,
                    general_enchants=general_enchants_ids,
                    not_recommended_enchants=not_recommended_enchants_ids,
                    memo=memo_content
                )
                messages.success(request, f"'{title_content}' 인챈트 추천이 성공적으로 저장되었습니다!")

                # 저장 성공 후 세션 완전히 초기화
                if 'recommended_enchants_ids' in request.session: del request.session['recommended_enchants_ids']
                if 'general_enchants_ids' in request.session: del request.session['general_enchants_ids']
                if 'not_recommended_enchants_ids' in request.session: del request.session[
                    'not_recommended_enchants_ids']
                if 'selected_item_type' in request.session: del request.session['selected_item_type']
                # 임시 제목/메모 초기화
                if 'temp_title' in request.session: del request.session['temp_title']
                if 'temp_memo' in request.session: del request.session['temp_memo']

                return redirect('enchant_recommender:list')

        # 세션에 변경된 분류 상태 저장
        request.session['recommended_enchants_ids'] = recommended_enchants_ids
        request.session['general_enchants_ids'] = general_enchants_ids
        request.session['not_recommended_enchants_ids'] = not_recommended_enchants_ids
        request.session['selected_item_type'] = selected_item_type

        return redirect('enchant_recommender:recommender')

    # GET 요청 처리 (페이지 처음 로드 또는 POST 후 리다이렉트 시)
    classified_ids = set(recommended_enchants_ids + general_enchants_ids + not_recommended_enchants_ids)
    available_enchants = get_applicable_enchants(selected_item_type, exclude_enchants_ids=list(classified_ids))

    context = {
        'item_types': ITEM_TYPES,
        'selected_item_type': selected_item_type,
        'selected_item_name': ITEM_TYPES.get(selected_item_type, "알 수 없는 아이템"),
        'all_enchants_data': ENCHANTMENTS,
        'available_enchants': available_enchants,
        'recommended_enchants_ids': recommended_enchants_ids,
        'general_enchants_ids': general_enchants_ids,
        'not_recommended_enchants_ids': not_recommended_enchants_ids,
        # 💡 임시 저장된 제목/메모 값을 템플릿으로 전달
        'temp_title': temp_title,
        'temp_memo': temp_memo,
    }

    return render(request, "enchant_recommender/recommender.html", context)

# --- 아래는 새로 추가된 뷰들입니다. (recommender_view 전문에는 포함되지 않지만, views.py 전체를 위해서는 필요) ---

def recommendation_list_view(request):
    recommendations = EnchantmentRecommendation.objects.all()
    context = {
        'recommendations': recommendations,
        'item_types': ITEM_TYPES,
        'ENCHANTMENTS': ENCHANTMENTS,
    }
    return render(request, "enchant_recommender/recommendation_list.html", context)

def recommendation_detail_view(request, pk):
    recommendation = get_object_or_404(EnchantmentRecommendation, pk=pk)

    recommended_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.recommended_enchants if ENCHANTMENTS.get(eid)]
    general_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.general_enchants if ENCHANTMENTS.get(eid)]
    not_recommended_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.not_recommended_enchants if ENCHANTMENTS.get(eid)]

    context = {
        'recommendation': recommendation,
        'item_type_name': ITEM_TYPES.get(recommendation.item_type, recommendation.item_type),
        'recommended_enchants': recommended_enchants_data,
        'general_enchants': general_enchants_data,
        'not_recommended_enchants': not_recommended_enchants_data,
    }
    return render(request, "enchant_recommender/recommendation_detail.html", context)
    # 저장된 ID 리스트를 실제 인챈트 데이터 객체 리스트로 변환
    recommended_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.recommended_enchants if
                                 ENCHANTMENTS.get(eid)]
    general_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.general_enchants if ENCHANTMENTS.get(eid)]
    not_recommended_enchants_data = [ENCHANTMENTS.get(eid) for eid in recommendation.not_recommended_enchants if
                                     ENCHANTMENTS.get(eid)]

    context = {
        'recommendation': recommendation,
        'item_type_name': ITEM_TYPES.get(recommendation.item_type, recommendation.item_type),
        'recommended_enchants': recommended_enchants_data,
        'general_enchants': general_enchants_data,
        'not_recommended_enchants': not_recommended_enchants_data,
    }
    return render(request, "enchant_recommender/recommendation_detail.html", context)