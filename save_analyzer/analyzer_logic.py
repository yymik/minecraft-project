# save_analyzer/analyzer_logic.py

import json

# 마인크래프트 바이옴 ID를 한글 이름으로 번역하기 위한 딕셔너리

ALL_CRITERIA_TRANSLATIONS = {
    # 🗺️ 모든 생물군계 (Biome)
    "minecraft:plains": "평원", "minecraft:sunflower_plains": "해바라기 평원", "minecraft:snowy_plains": "눈 덮인 평원",
    "minecraft:ice_spikes": "얼음 가시", "minecraft:desert": "사막", "minecraft:savanna": "사바나",
    "minecraft:savanna_plateau": "사바나 고원", "minecraft:windswept_savanna": "바람이 세찬 사바나",
    "minecraft:forest": "숲", "minecraft:flower_forest": "꽃 숲", "minecraft:birch_forest": "자작나무 숲",
    "minecraft:dark_forest": "어두운 숲", "minecraft:old_growth_birch_forest": "원시 자작나무 숲",
    "minecraft:old_growth_pine_taiga": "원시 소나무 타이가", "minecraft:old_growth_spruce_taiga": "원시 가문비나무 타이가",
    "minecraft:taiga": "타이가", "minecraft:snowy_taiga": "눈 덮인 타이가", "minecraft:swamp": "늪",
    "minecraft:mangrove_swamp": "맹그로브 늪", "minecraft:jungle": "정글", "minecraft:sparse_jungle": "희소한 정글",
    "minecraft:bamboo_jungle": "대나무 정글", "minecraft:windswept_hills": "바람이 세찬 언덕",
    "minecraft:windswept_gravelly_hills": "바람이 세찬 자갈 언덕", "minecraft:windswept_forest": "바람이 세찬 숲",
    "minecraft:cherry_grove": "벚나무 숲", "minecraft:stony_shore": "돌 해안", "minecraft:snowy_beach": "눈 덮인 해변",
    "minecraft:beach": "해변", "minecraft:river": "강", "minecraft:frozen_river": "언 강",
    "minecraft:ocean": "바다", "minecraft:deep_ocean": "깊은 바다", "minecraft:cold_ocean": "차가운 바다",
    "minecraft:deep_cold_ocean": "깊고 차가운 바다", "minecraft:lukewarm_ocean": "미지근한 바다",
    "minecraft:deep_lukewarm_ocean": "깊고 미지근한 바다", "minecraft:warm_ocean": "따뜻한 바다",
    "minecraft:frozen_ocean": "언 바다", "minecraft:deep_frozen_ocean": "깊고 언 바다",
    "minecraft:mushroom_fields": "버섯 들판", "minecraft:dripstone_caves": "점적석 동굴", "minecraft:lush_caves": "무성한 동굴",
    "minecraft:nether_wastes": "네더 황무지", "minecraft:warped_forest": "뒤틀린 숲", "minecraft:crimson_forest": "진홍빛 숲",
    "minecraft:soul_sand_valley": "영혼 모래 골짜기", "minecraft:basalt_deltas": "현무암 삼각주",
    "minecraft:the_end": "디 엔드", "minecraft:small_end_islands": "작은 엔드 섬", "minecraft:end_midlands": "엔드 중지",
    "minecraft:end_highlands": "엔드 고지", "minecraft:end_barrens": "엔드 불모지",
    "minecraft:stony_peaks": "돌 봉우리", "minecraft:jagged_peaks": "뾰족한 봉우리", "minecraft:frozen_peaks": "얼어붙은 봉우리",
    "minecraft:snowy_slopes": "눈 덮인 경사면", "minecraft:grove": "수목 지대", "minecraft:meadow": "목초지",
    "minecraft:pale_garden": "창백한 정원",

    "minecraft:oak_log": "참나무 원목", "minecraft:savanna_biome": "사바나 생물군계", "minecraft:jungle_biome": "정글 생물군계",
    "minecraft:strider": "스트라이더", "minecraft:piglin_brute": "피글린 야수",

    # 🍖 균형 잡힌 식단 (Balanced Diet) - 접두사 없음
    "apple": "사과", "baked_potato": "구운 감자", "beef": "익히지 않은 소고기", "beetroot": "비트",
    "beetroot_soup": "비트 수프", "bread": "빵", "carrot": "당근", "chicken": "익히지 않은 닭고기",
    "chorus_fruit": "후렴과", "cooked_beef": "스테이크", "cooked_chicken": "익힌 닭고기",
    "cooked_cod": "익힌 대구", "cooked_mutton": "익힌 양고기", "cooked_porkchop": "익힌 돼지고기",
    "cooked_rabbit": "익힌 토끼고기", "cooked_salmon": "익힌 연어", "cookie": "쿠키",
    "dried_kelp": "마른 켈프", "enchanted_golden_apple": "마법이 부여된 황금 사과", "golden_apple": "황금 사과",
    "golden_carrot": "황금 당근", "honey_bottle": "꿀이 든 병", "melon_slice": "수박",
    "mutton": "익히지 않은 양고기", "mushroom_stew": "버섯 스튜", "poisonous_potato": "독이 있는 감자",
    "porkchop": "익히지 않은 돼지고기", "potato": "감자", "pufferfish": "복어", "pumpkin_pie": "호박 파이",
    "rabbit": "익히지 않은 토끼고기", "rabbit_stew": "토끼 스튜", "rotten_flesh": "썩은 살점", "salmon": "생 연어",
    "spider_eye": "거미 눈", "suspicious_stew": "수상한 스튜", "sweet_berries": "달콤한 열매",
    "tropical_fish": "열대어", "cod": "생 대구", "glow_berries": "발광 열매", "raw_cod": "생 대구",
    "raw_salmon": "생 연어", "cooked_fished": "익힌 물고기",

    # 💀 몬스터 도감 (Kill All Mobs) - 'minecraft:' 접두사 통일 및 새 항목 추가
    "minecraft:allay": "알레이", "minecraft:axolotl": "아홀로틀", "minecraft:blaze": "블레이즈",
    "minecraft:cave_spider": "동굴 거미", "minecraft:creeper": "크리퍼", "minecraft:drowned": "드라운드",
    "minecraft:elder_guardian": "엘더 가디언", "minecraft:enderman": "엔더맨", "minecraft:endermite": "엔더마이트",
    "minecraft:evoker": "소환사", "minecraft:ghast": "가스트", "minecraft:guardian": "가디언",
    "minecraft:hoglin": "호글린", "minecraft:husk": "허스크", "minecraft:magma_cube": "마그마 큐브",
    "minecraft:phantom": "팬텀", "minecraft:piglin": "피글린", "minecraft:piglin_brute": "피글린 야수",
    "minecraft:pillager": "약탈자", "minecraft:ravager": "파괴수", "minecraft:shulker": "셜커",
    "minecraft:silverfish": "좀벌레", "minecraft:skeleton": "스켈레톤", "minecraft:slime": "슬라임",
    "minecraft:spider": "거미", "minecraft:stray": "스트레이", "minecraft:vex": "벡스", "minecraft:vindicator": "변명자",
    "minecraft:witch": "마녀", "minecraft:wither": "위더", "minecraft:wither_skeleton": "위더 스켈레톤",
    "minecraft:zoglin": "조글린", "minecraft:zombie": "좀비", "minecraft:zombie_villager": "좀비 주민",
    "minecraft:zombified_piglin": "좀비화된 피글린", "minecraft:bat": "박쥐", "minecraft:camel": "낙타",
    "minecraft:donkey": "당나귀", "minecraft:frog": "개구리", "minecraft:glow_squid": "빛나는 오징어",
    "minecraft:horse": "말", "minecraft:llama": "라마", "minecraft:mooshroom": "무시룸", "minecraft:mule": "노새",
    "minecraft:ocelot": "오실롯", "minecraft:parrot": "앵무새", "minecraft:polar_bear": "북극곰", "minecraft:sniffer": "스니퍼",
    "minecraft:squid": "오징어", "minecraft:trader_llama": "떠돌이 상인의 라마", "minecraft:turtle": "거북",
    "minecraft:ender_dragon": "엔더 드래곤", "minecraft:bogged": "보그드", "minecraft:breeze": "브리즈",
    "minecraft:crafter": "크리커",  # 크리킹은 크리커의 오타로 추정
    "minecraft:husk": "허스크",  # 중복 방지
    "minecraft:ravager": "파괴수",  # 중복 방지
    "minecraft:vindicator": "변명자",  # 중복 방지
    "minecraft:wither_skeleton": "위더 스켈레톤",  # 중복 방지

    # 🐑 동물 종류 (Bred All Animals) 및 🐺 늑대 종류 (Whole Pack)
    "minecraft:armadillo": "아르마딜로", "minecraft:cat": "고양이", "minecraft:chicken": "닭",
    "minecraft:cow": "소", "minecraft:donkey": "당나귀", "minecraft:fox": "여우", "minecraft:frog": "개구리",
    "minecraft:hoglin": "호글린", "minecraft:horse": "말", "minecraft:llama": "라마", "minecraft:mooshroom": "무시룸",
    "minecraft:mule": "노새", "minecraft:ocelot": "오실롯", "minecraft:panda": "판다", "minecraft:pig": "돼지",
    "minecraft:rabbit": "토끼", "minecraft:sheep": "양", "minecraft:sniffer": "스니퍼", "minecraft:strider": "스트라이더",
    "minecraft:turtle": "거북", "minecraft:wolf": "늑대", "minecraft:goat": "염소", "minecraft:axolotl": "아홀로틀",
    "minecraft:bee": "벌",

    # 늑대 종류 (Whole Pack)
    "minecraft:snowy": "눈 덮인 늑대", "minecraft:forest_wolf": "숲 늑대", "minecraft:ashen": "잿빛 늑대",
    "minecraft:rusty": "녹슨 늑대", "minecraft:spotted": "점박이 늑대", "minecraft:striped": "줄무늬 늑대",
    "minecraft:woods": "수풀 늑대", "minecraft:chestnut": "밤나무색 늑대", "minecraft:pale": "창백한 늑대",
    "minecraft:black": "검은색 늑대",

    # 🌈 염료 종류 (Complete Catalogue)
    "minecraft:white": "흰색 염료", "minecraft:light_gray": "밝은 회색 염료", "minecraft:gray": "회색 염료",
    "minecraft:black": "검은색 염료", "minecraft:brown": "갈색 염료", "minecraft:red": "빨간색 염료",
    "minecraft:orange": "주황색 염료", "minecraft:yellow": "노란색 염료", "minecraft:lime": "연두색 염료",
    "minecraft:green": "초록색 염료", "minecraft:cyan": "청록색 염료", "minecraft:light_blue": "밝은 파란색 염료",
    "minecraft:blue": "파란색 염료", "minecraft:purple": "보라색 염료", "minecraft:magenta": "자홍색 염료",
    "minecraft:pink": "분홍색 염료",

    "minecraft:warped_forest_2": "뒤틀린 숲 2",
}

# --------------------------------------------------------
# 🎯 ADVANCEMENT_CRITERIA_SETS: 도전과제별 전체 항목 정의 (순서 오류 방지 위해 이 섹션을 상단에 정의)
# --------------------------------------------------------
ADVANCEMENT_CRITERIA_SETS = {
    # 모험의 시간 (생략 - 이전에 71개로 정의됨)
    "minecraft:adventure/adventuring_time": [
        "minecraft:plains", "minecraft:sunflower_plains", "minecraft:snowy_plains", "minecraft:ice_spikes",
        "minecraft:desert", "minecraft:savanna",
        "minecraft:savanna_plateau", "minecraft:windswept_savanna", "minecraft:forest", "minecraft:flower_forest",
        "minecraft:birch_forest",
        "minecraft:dark_forest", "minecraft:old_growth_birch_forest", "minecraft:old_growth_pine_taiga",
        "minecraft:old_growth_spruce_taiga",
        "minecraft:taiga", "minecraft:snowy_taiga", "minecraft:swamp", "minecraft:mangrove_swamp", "minecraft:jungle",
        "minecraft:sparse_jungle",
        "minecraft:bamboo_jungle", "minecraft:windswept_hills", "minecraft:windswept_gravelly_hills",
        "minecraft:windswept_forest",
        "minecraft:cherry_grove", "minecraft:stony_shore", "minecraft:snowy_beach", "minecraft:beach",
        "minecraft:river",
        "minecraft:frozen_river", "minecraft:ocean", "minecraft:deep_ocean", "minecraft:cold_ocean",
        "minecraft:deep_cold_ocean",
        "minecraft:lukewarm_ocean", "minecraft:deep_lukewarm_ocean", "minecraft:warm_ocean", "minecraft:frozen_ocean",
        "minecraft:deep_frozen_ocean",
        "minecraft:mushroom_fields", "minecraft:dripstone_caves", "minecraft:lush_caves", "minecraft:nether_wastes",
        "minecraft:warped_forest",
        "minecraft:crimson_forest", "minecraft:soul_sand_valley", "minecraft:basalt_deltas", "minecraft:the_end",
        "minecraft:small_end_islands", "minecraft:end_midlands", "minecraft:end_highlands", "minecraft:end_barrens",
        "minecraft:stony_peaks", "minecraft:jagged_peaks", "minecraft:frozen_peaks", "minecraft:snowy_slopes",
        "minecraft:grove",
        "minecraft:meadow", "minecraft:pale_garden"
    ],

    # 짝지어주기 (Bred All Animals) - 21개 항목으로 확정 (요청하신 목록 기준)
    "minecraft:husbandry/bred_all_animals": [
        "minecraft:pig", "minecraft:cow", "minecraft:mooshroom", "minecraft:chicken", "minecraft:sheep",
        "minecraft:rabbit", "minecraft:horse", "minecraft:llama", "minecraft:cat", "minecraft:ocelot",
        "minecraft:bee", "minecraft:wolf", "minecraft:turtle", "minecraft:panda", "minecraft:fox",
        "minecraft:hoglin", "minecraft:strider", "minecraft:donkey", "minecraft:mule", "minecraft:axolotl",
        "minecraft:goat",
    ],

    # 균형 잡힌 식단 (Balanced Diet) - 40개 항목 (생략 - 이전 목록 유지)
    "minecraft:husbandry/balanced_diet": [
        "apple", "cooked_beef", "cooked_chicken", "cooked_cod", "cooked_mutton", "cooked_porkchop", "cooked_rabbit",
        "cooked_salmon",
        "cookie", "mushroom_stew", "rabbit_stew", "beetroot_soup", "suspicious_stew", "cod", "salmon", "tropical_fish",
        "pufferfish", "beef", "chicken", "mutton", "porkchop", "rabbit", "bread", "carrot", "potato",
        "baked_potato", "poisonous_potato", "golden_apple", "enchanted_golden_apple", "golden_carrot", "melon_slice",
        "pumpkin_pie", "sweet_berries", "glow_berries", "chorus_fruit", "dried_kelp", "honey_bottle", "rotten_flesh",
        "spider_eye", "beetroot"
    ],

    # 몬스터 도감 (Kill All Mobs) - 37개 항목으로 확정 (요청하신 목록 기준)
    "minecraft:adventure/kill_all_mobs": [
        "minecraft:guardian", "minecraft:ghast", "minecraft:spider", "minecraft:cave_spider", "minecraft:magma_cube",
        "minecraft:witch", "minecraft:vindicator", "minecraft:blaze", "minecraft:shulker", "minecraft:evoker",
        "minecraft:skeleton", "minecraft:stray", "minecraft:slime", "minecraft:enderman", "minecraft:wither_skeleton",
        "minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:creeper", "minecraft:phantom",
        "minecraft:pillager", "minecraft:ravager", "minecraft:vex", "minecraft:endermite", "minecraft:elder_guardian",
        "minecraft:wither", "minecraft:zoglin", "minecraft:piglin", "minecraft:hoglin", "minecraft:zombified_piglin",
        "minecraft:piglin_brute", "minecraft:bogged", "minecraft:breeze", "minecraft:ender_dragon",
        "minecraft:silverfish",
        "minecraft:zombie_villager", "minecraft:axolotl"
    ],

    "minecraft:husbandry/whole_pack": [
        "minecraft:snowy", "minecraft:forest", "minecraft:ashen", "minecraft:rusty", "minecraft:spotted",
        "minecraft:striped", "minecraft:woods", "minecraft:chestnut", "minecraft:pale", "minecraft:black"
    ],

    "minecraft:husbandry/complete_catalogue": [
        "minecraft:white", "minecraft:light_gray", "minecraft:gray", "minecraft:black", "minecraft:brown",
        "minecraft:red",
        "minecraft:orange", "minecraft:yellow", "minecraft:lime", "minecraft:green", "minecraft:cyan",
        "minecraft:light_blue", "minecraft:blue", "minecraft:purple", "minecraft:magenta", "minecraft:pink"
    ],

    "minecraft:nether/explore_nether": [
        "minecraft:nether_wastes", "minecraft:warped_forest", "minecraft:crimson_forest", "minecraft:soul_sand_valley",
        "minecraft:basalt_deltas"
    ]
}

ADVANCEMENT_DEFAULTS = {
    # total은 ADVANCEMENT_CRITERIA_SETS의 길이로 자동 계산 (오류 해결)
    "minecraft:adventure/adventuring_time": {
        "total": len(ADVANCEMENT_CRITERIA_SETS["minecraft:adventure/adventuring_time"]), "name": "모험의 시간"},
    "minecraft:husbandry/balanced_diet": {"total": len(ADVANCEMENT_CRITERIA_SETS["minecraft:husbandry/balanced_diet"]),
                                          "name": "균형 잡힌 식단"},

    "minecraft:adventure/kill_all_mobs": {"total": 37, "name": "몬스터 도감"},  # 37개로 확정
    "minecraft:husbandry/bred_all_animals": {"total": 21, "name": "짝지어주기"},  # 21개로 확정

    "minecraft:husbandry/whole_pack": {"total": 9, "name": "하나의 늑대 무리"},
    "minecraft:husbandry/complete_catalogue": {"total": 16, "name": "완벽한 카탈로그"},
    "minecraft:nether/explore_nether": {"total": 5, "name": "지옥 속으로"},
}

ADVANCEMENT_DEFAULTS = {
    # total은 ADVANCEMENT_CRITERIA_SETS의 길이로 자동 계산 (오류 해결)
    "minecraft:adventure/adventuring_time": {
        "total": len(ADVANCEMENT_CRITERIA_SETS["minecraft:adventure/adventuring_time"]), "name": "모험의 시간"},
    "minecraft:husbandry/balanced_diet": {"total": len(ADVANCEMENT_CRITERIA_SETS["minecraft:husbandry/balanced_diet"]),
                                          "name": "균형 잡힌 식단"},
    "minecraft:adventure/kill_all_mobs": {"total": len(ADVANCEMENT_CRITERIA_SETS["minecraft:adventure/kill_all_mobs"]),
                                          "name": "몬스터 도감"},  # 이름 변경
    "minecraft:husbandry/bred_all_animals": {"total": 21, "name": "짝지어주기"},  # 이름 변경
    "minecraft:husbandry/whole_pack": {"total": 9, "name": "하나의 늑대 무리"},
    "minecraft:husbandry/complete_catalogue": {"total": 16, "name": "완벽한 카탈로그"},
    "minecraft:nether/explore_nether": {"total": 5, "name": "지옥 속으로"},
}

def clean_and_translate_criteria(criteria_key):
    # cleaned_key = criteria_key.replace("minecraft:", "")
    # return ALL_CRITERIA_TRANSLATIONS.get(cleaned_key, criteria_key)

    # 수정 후: 딕셔너리에서 원본 키(minecraft: 포함)를 찾고,
    #          실패 시 (접두사가 붙은) 원본 키를 반환 (번역 실패 시 최소한 키는 보여줌)
    return ALL_CRITERIA_TRANSLATIONS.get(criteria_key, criteria_key)


# save_analyzer/analyzer_logic.py 내의 analyze_advancements_from_content 함수만 아래와 같이 수정

def analyze_advancements_from_content(json_content_str):
    try:
        data = json.loads(json_content_str)
    except json.JSONDecodeError:
        return {"error": "JSON 파일 형식이 올바르지 않습니다. 파일이 손상되었거나 다른 형식의 파일일 수 있습니다."}

    if "DataVersion" not in data:
        return {"error": "유효한 마인크래프트 발전 과제 파일이 아닙니다."}

    results = {
        "completed": [],
        "in_progress": [],
        "details": {}
    }

    all_advancement_ids = set(data.keys())

    for adv_id, default_info in ADVANCEMENT_DEFAULTS.items():
        if adv_id in all_advancement_ids:
            adv_data = data[adv_id]
            criteria = adv_data.get("criteria", {})
            done = adv_data.get("done", False)

            completed_keys = set(criteria.keys())

            # 1. 전체 기준 세트 가져오기 (ADVANCEMENT_CRITERIA_SETS 참조)
            total_keys = set(ADVANCEMENT_CRITERIA_SETS.get(adv_id, []))

            # 2. 완료된 항목과 미완료된 항목을 통합하여 목록 생성
            all_translated_list = []

            # 모든 가능한 키를 순회
            for key in total_keys:
                is_done = key in completed_keys
                all_translated_list.append({
                    "name": clean_and_translate_criteria(key),
                    "done": is_done,
                    "sort_key": clean_and_translate_criteria(key)
                })

            # JSON에만 있고 ADVANCEMENT_CRITERIA_SETS에 없는 항목도 처리 (예: 레거시)
            for key in completed_keys - total_keys:
                all_translated_list.append({
                    "name": clean_and_translate_criteria(key),
                    "done": True,
                    "sort_key": clean_and_translate_criteria(key),
                    "extra": True
                })

            # 체크순으로정렬
            all_translated_list.sort(key=lambda x: (x['done'], x['sort_key']), reverse=True)

            if not done:
                results["details"][adv_id.split('/')[-1]] = {
                    "name": default_info["name"],
                    "all_items": all_translated_list,  # 미완료/완료 통합 목록
                    "count": len(completed_keys),
                    "total": len(total_keys) if len(total_keys) > 0 else default_info["total"],
                }

            if done:
                results["completed"].append(default_info["name"])
            elif adv_id not in results["details"]:
                results["in_progress"].append(default_info["name"])

    # ADVANCEMENT_DEFAULTS에 없는 미완료된 도전과제 처리 (범용 로직)
    for adv_id, adv_data in data.items():
        if adv_id.startswith("minecraft:recipe") or adv_id == "DataVersion":
            continue

        adv_name = adv_id.split('/')[-1]

        if adv_id.split('/')[-1] in results["details"] or adv_data.get("done", False):
            if adv_data.get("done", False) and adv_name not in results["completed"]:
                results["completed"].append(adv_name)
            continue

        if not adv_data.get("done", False):
            criteria = adv_data.get("criteria", {})
            completed_keys = set(criteria.keys())

            # 범용 로직: 완료된 항목만 표시
            all_translated_list = []
            for key in completed_keys:
                all_translated_list.append({
                    "name": clean_and_translate_criteria(key),
                    "done": True,
                    "sort_key": clean_and_translate_criteria(key)
                })
            all_translated_list.sort(key=lambda x: x['sort_key'])

            results["details"][adv_name] = {
                "name": adv_name.replace('_', ' ').title(),
                "all_items": all_translated_list,
                "count": len(completed_keys),
                "total": "알 수 없음",
                "generic": True
            }
            results["in_progress"].append(adv_name.replace('_', ' ').title())

    completed_count = len(results["completed"])
    total_advancements = len(all_advancement_ids) - len(
        [k for k in all_advancement_ids if k.startswith("minecraft:recipe") or k == "DataVersion"])

    results['summary'] = {
        'completed_count': completed_count,
        'total_count': total_advancements,
        'progress_percentage': (completed_count / total_advancements * 100) if total_advancements > 0 else 0
    }

    return results