# save_analyzer/analyzer_logic.py

import json

# 마인크래프트 바이옴 ID를 한글 이름으로 번역하기 위한 딕셔너리
BIOME_TRANSLATIONS = {
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
    "minecraft:pale_garden": "창백한 정원"
}

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

    for adv_id, adv_data in data.items():
        if adv_id.startswith("minecraft:recipe") or adv_id == "DataVersion":
            continue

        adv_name = adv_id.split('/')[-1]

        if adv_data.get("done", False):
            results["completed"].append(adv_name)
        else:
            results["in_progress"].append(adv_name)

        if adv_id == "minecraft:adventure/adventuring_time":
            criteria = adv_data.get("criteria", {})
            visited_biomes = [BIOME_TRANSLATIONS.get(b, b.replace("minecraft:", "")) for b in criteria.keys()]
            results["details"]["adventuring_time"] = {
                "visited": sorted(visited_biomes), "count": len(visited_biomes), "total": 51
            }

        if adv_id == "minecraft:husbandry/balanced_diet":
            criteria = adv_data.get("criteria", {})
            eaten_foods = [food.replace("minecraft:", "") for food in criteria.keys()]
            results["details"]["balanced_diet"] = {
                "eaten": sorted(eaten_foods), "count": len(eaten_foods), "total": 40
            }

        if adv_id == "minecraft:adventure/kill_all_mobs":
            criteria = adv_data.get("criteria", {})
            killed_mobs = [m.replace("minecraft:", "") for m in criteria.keys()]
            results["details"]["kill_all_mobs"] = {
                "killed": sorted(killed_mobs), "count": len(killed_mobs), "total": 25
            }

    completed_count = len(results["completed"])
    total_advancements = completed_count + len(results["in_progress"])
    
    results['summary'] = {
        'completed_count': completed_count,
        'total_count': total_advancements,
        'progress_percentage': (completed_count / total_advancements * 100) if total_advancements > 0 else 0
    }
    
    return results