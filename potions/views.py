from django.shortcuts import render, redirect

# from django.templatetags.static import static # 뷰에서는 직접 잘 안쓰임. 템플릿에서 {% load static %} 사용

# --- 데이터 정의 (이 부분은 매우 깁니다. 이전 답변의 전체 ITEMS, RECIPES를 여기에 넣어야 합니다) ---
ITEMS = {
    # === 베이스 아이템 (물병) ===
    "water_bottle": {"id": "water_bottle", "name": "물병", "description": "모든 물약의 시작점입니다.", "image": "potions/images/water_bottle.png", "type": "base_potion"},

    # === 기초 물약 (물병 + 재료1) ===
    "awkward_potion": {"id": "awkward_potion", "name": "어색한 물약", "description": "효과 없음 (대부분 효과 물약의 베이스)", "image": "potions/images/awkward_potion.png", "type": "potion"},
    "mundane_potion": {"id": "mundane_potion", "name": "평범한 물약", "description": "효과 없음. (레드스톤 가루로 제작)", "image": "potions/images/water_bottle.png", "type": "potion"},
    "thick_potion": {"id": "thick_potion", "name": "진한 물약", "description": "효과 없음. (발광석 가루로 제작)", "image": "potions/images/thick_potion.png", "type": "potion"},
    "potion_of_weakness_base": {"id": "potion_of_weakness_base", "name": "나약함의 물약 (1:30)", "description": "플레이어의 접근전 공격 피해가 4만큼 줄어듦.", "image": "potions/images/potion_of_weakness_base.gif", "type": "potion"},

    # === 효과 물약 (어색한 물약 + 재료2) ===
    "potion_of_swiftness": {"id": "potion_of_swiftness", "name": "신속의 물약 (3:00)", "description": "신속: 이동 속도, 달리기 속도, 점프 거리를 약 20% 향상.", "image": "potions/images/potion_of_swiftness.gif", "type": "potion"},
    "potion_of_leaping": {"id": "potion_of_leaping", "name": "도약의 물약 (3:00)", "description": "점프 강화: 플레이어가 ½ 블록을 더 높이 점프할 수 있음.", "image": "potions/images/potion_of_leaping.gif", "type": "potion"},
    "potion_of_healing": {"id": "potion_of_healing", "name": "치유의 물약", "description": "즉시 치유: 물약 한 병당 4 회복.", "image": "potions/images/potion_of_healing.gif", "type": "potion"},
    "potion_of_poison": {"id": "potion_of_poison", "name": "독의 물약 (0:45)", "description": "독: 플레이어가 매 2.5초 마다 1의 피해를 입는다. (체력 1 미만으로 감소 안 함)", "image": "potions/images/potion_of_poison.gif", "type": "potion"},
    "potion_of_water_breathing": {"id": "potion_of_water_breathing", "name": "수중 호흡의 물약 (3:00)", "description": "수중 호흡: 물속에 있어도 산소 막대가 줄어들지 않음.", "image": "potions/images/potion_of_water_breathing.gif", "type": "potion"},
    "potion_of_fire_resistance": {"id": "potion_of_fire_resistance", "name": "화염 저항의 물약 (3:00)", "description": "화염 저항: 화염, 용암, 마그마 블록, 원거리 블레이즈 공격에 내성이 생김.", "image": "potions/images/potion_of_fire_resistance.gif", "type": "potion"},
    "potion_of_night_vision": {"id": "potion_of_night_vision", "name": "야간 투시의 물약 (3:00)", "description": "야간 투시: 물 속을 포함해 모든 곳이 최대 밝기 수준으로 보임.", "image": "potions/images/potion_of_night_vision.gif", "type": "potion"},
    "potion_of_strength": {"id": "potion_of_strength", "name": "힘의 물약 (3:00)", "description": "힘: 플레이어의 접근전 공격 피해를 3 증가.", "image": "potions/images/potion_of_strength.gif", "type": "potion"},
    "potion_of_regeneration": {"id": "potion_of_regeneration", "name": "재생의 물약 (0:45)", "description": "재생: 매 2.5초 마다 생명력 1 회복.", "image": "potions/images/potion_of_regeneration.gif", "type": "potion"},
    "potion_of_the_turtle_master": {"id": "potion_of_the_turtle_master", "name": "거북 도사의 물약 (0:20)", "description": "감속 IV, 저항 III: 플레이어의 속도가 60% 감소, 피해를 60%만 받음.", "image": "potions/images/potion_of_the_turtle_master.gif", "type": "potion"},
    "potion_of_slow_falling": {"id": "potion_of_slow_falling", "name": "느린 낙하의 물약 (1:30)", "description": "느린 낙하: 플레이어가 천천히 떨어지며, 땅에 닿을 때 피해를 받지 않음.", "image": "potions/images/potion_of_slow_falling.gif", "type": "potion"},

    # === 기간 연장 물약 ===
    "potion_of_fire_resistance_long": {"id": "potion_of_fire_resistance_long", "name": "화염 저항의 물약 (8:00)", "description": "화염 저항: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_fire_resistance.gif", "type": "potion"},
    "potion_of_regeneration_long": {"id": "potion_of_regeneration_long", "name": "재생의 물약 (1:30)", "description": "재생: (효과 동일, 지속 시간 1:30)", "image": "potions/images/potion_of_regeneration.gif", "type": "potion"},
    "potion_of_strength_long": {"id": "potion_of_strength_long", "name": "힘의 물약 (8:00)", "description": "힘: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_strength.gif", "type": "potion"},
    "potion_of_swiftness_long": {"id": "potion_of_swiftness_long", "name": "신속의 물약 (8:00)", "description": "신속: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_swiftness.gif", "type": "potion"},
    "potion_of_night_vision_long": {"id": "potion_of_night_vision_long", "name": "야간 투시의 물약 (8:00)", "description": "야간 투시: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_night_vision.gif", "type": "potion"},
    "potion_of_invisibility_long": {"id": "potion_of_invisibility_long", "name": "투명화 물약 (8:00)", "description": "투명: 플레이어가 안보이게 됨. 장비/갑옷은 계속 보임. (지속 시간 8:00)", "image": "potions/images/potion_of_invisibility.gif", "type": "potion"}, # 베이스: potion_of_invisibility
    "potion_of_water_breathing_long": {"id": "potion_of_water_breathing_long", "name": "수중 호흡의 물약 (8:00)", "description": "수중 호흡: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_water_breathing.gif", "type": "potion"},
    "potion_of_leaping_long": {"id": "potion_of_leaping_long", "name": "도약의 물약 (8:00)", "description": "점프 강화: (효과 동일, 지속 시간 8:00)", "image": "potions/images/potion_of_leaping.gif", "type": "potion"},
    "potion_of_slow_falling_long": {"id": "potion_of_slow_falling_long", "name": "느린 낙하의 물약 (4:00)", "description": "느린 낙하: (효과 동일, 지속 시간 4:00)", "image": "potions/images/potion_of_slow_falling.gif", "type": "potion"},
    "potion_of_poison_long": {"id": "potion_of_poison_long", "name": "독의 물약 (1:30)", "description": "독: (효과 동일, 지속 시간 1:30)", "image": "potions/images/potion_of_poison.gif", "type": "potion"},
    "potion_of_weakness_long": {"id": "potion_of_weakness_long", "name": "나약함의 물약 (4:00)", "description": "나약함: (효과 동일, 지속 시간 4:00)", "image": "potions/images/potion_of_weakness_base.gif", "type": "potion"}, # 베이스: potion_of_weakness_base
    "potion_of_slowness_long": {"id": "potion_of_slowness_long", "name": "감속의 물약 (4:00)", "description": "감속: 해당 시간 동안 속도가 15%로 느려짐. (지속 시간 4:00)", "image": "potions/images/potion_of_slowness.gif", "type": "potion"}, # 베이스: potion_of_slowness
    "potion_of_the_turtle_master_long": {"id": "potion_of_the_turtle_master_long", "name": "거북 도사의 물약 (0:40)", "description": "감속 IV, 저항 III: (효과 동일, 지속 시간 0:40)", "image": "potions/images/potion_of_the_turtle_master.gif", "type": "potion"},

    # === 강화 물약 ===
    "potion_of_healing_strong": {"id": "potion_of_healing_strong", "name": "치유의 물약 II", "description": "즉시 치유 II: 물약 한 병당 8 회복.", "image": "potions/images/potion_of_healing.gif", "type": "potion"},
    "potion_of_regeneration_strong": {"id": "potion_of_regeneration_strong", "name": "재생의 물약 II (0:22)", "description": "재생 II: 매 1.2초 마다 생명력 1 회복.", "image": "potions/images/potion_of_regeneration.gif", "type": "potion"},
    "potion_of_strength_strong": {"id": "potion_of_strength_strong", "name": "힘의 물약 II (1:30)", "description": "힘 II: 플레이어의 접근전 공격 피해를 6 증가.", "image": "potions/images/potion_of_strength.gif", "type": "potion"},
    "potion_of_swiftness_strong": {"id": "potion_of_swiftness_strong", "name": "신속의 물약 II (1:30)", "description": "신속 II: 이동 속도, 달리기 속도, 점프 거리를 약 40% 향상.", "image": "potions/images/potion_of_swiftness.gif", "type": "potion"},
    "potion_of_leaping_strong": {"id": "potion_of_leaping_strong", "name": "도약의 물약 II (1:30)", "description": "점프 강화 II: 플레이어가 1 ¼ 블록을 더 높이 점프할 수 있음.", "image": "potions/images/potion_of_leaping.gif", "type": "potion"},
    "potion_of_poison_strong": {"id": "potion_of_poison_strong", "name": "독의 물약 II (0:21)", "description": "독 II: 플레이어가 1.2초 마다 1의 피해를 입는다.", "image": "potions/images/potion_of_poison.gif", "type": "potion"},
    "potion_of_harming_strong": {"id": "potion_of_harming_strong", "name": "고통의 물약 II", "description": "즉시 피해 II: 12의 피해를 입힌다.", "image": "potions/images/potion_of_harming.gif", "type": "potion"}, # 베이스: potion_of_harming
    "potion_of_slowness_strong": {"id": "potion_of_slowness_strong", "name": "감속의 물약 IV (0:20)", "description": "감속 IV: 해당 시간 동안 속도가 60%로 느려짐.", "image": "potions/images/potion_of_slowness.gif", "type": "potion"}, # 베이스: potion_of_slowness_long (주의: 실제 마크에선 직접 강화가 아님)
    "potion_of_the_turtle_master_strong": {"id": "potion_of_the_turtle_master_strong", "name": "거북 도사의 물약 II (0:20)", "description": "감속 VI, 저항 IV: 플레이어의 속도가 90%로 느려지고, 피해는 80%만 받음.", "image": "potions/images/potion_of_the_turtle_master.gif", "type": "potion"},

    # === 부패/변형 물약 ===
    "potion_of_slowness": {"id": "potion_of_slowness", "name": "감속의 물약 (1:30)", "description": "(베이스: 신속 또는 도약) 감속: 해당 시간 동안 이동 속도가 15% 감소.", "image": "potions/images/potion_of_slowness.gif", "type": "potion"},
    "potion_of_harming": {"id": "potion_of_harming", "name": "고통의 물약", "description": "(베이스: 치유 또는 독) 즉시 피해: 6의 피해를 입힌다.", "image": "potions/images/potion_of_harming.gif", "type": "potion"},
    "potion_of_invisibility": {"id": "potion_of_invisibility", "name": "투명화 물약 (3:00)", "description": "(베이스: 야간 투시) 투명: 플레이어가 안보이게 됨. 장비/갑옷은 계속 보임.", "image": "potions/images/potion_of_invisibility.gif", "type": "potion"},
    "potion_of_weakness_from_effect": {"id": "potion_of_weakness_from_effect", "name": "나약함의 물약 (1:30)", "description": "(베이스: 힘 또는 재생) 나약함.", "image": "potions/images/potion_of_weakness_base.gif", "type": "potion"}, # potion_of_weakness_base와 구분

    # === 투척용 물약 (ID: {base_id}_splash) ===
    "potion_of_swiftness_splash": {"id": "potion_of_swiftness_splash", "name": "투척용 신속의 물약 (3:00)", "description": "투척용: 신속 효과", "image": "potions/images/potion_of_swiftness.gif", "type": "potion_splash"},
    "potion_of_healing_splash": {"id": "potion_of_healing_splash", "name": "투척용 치유의 물약", "description": "투척용: 즉시 치유", "image": "potions/images/potion_of_healing.gif", "type": "potion_splash"},
    "potion_of_poison_splash": {"id": "potion_of_poison_splash", "name": "투척용 독의 물약 (0:45)", "description": "투척용: 독 효과", "image": "potions/images/potion_of_poison.gif", "type": "potion_splash"},
    # ... (다른 모든 효과 물약의 _splash 버전 추가) ...
    "potion_of_harming_splash": {"id": "potion_of_harming_splash", "name": "투척용 고통의 물약", "description": "투척용: 즉시 피해", "image": "potions/images/potion_of_harming.gif", "type": "potion_splash"},


    # === 잔류형 물약 (ID: {base_id}_lingering) ===
    "potion_of_swiftness_lingering": {"id": "potion_of_swiftness_lingering", "name": "잔류형 신속의 물약", "description": "잔류형: 신속 효과 구름", "image": "potions/images/potion_of_swiftness.gif", "type": "potion_lingering"},
    "potion_of_healing_lingering": {"id": "potion_of_healing_lingering", "name": "잔류형 치유의 물약", "description": "잔류형: 치유 효과 구름", "image": "potions/images/potion_of_healing.gif", "type": "potion_lingering"},
    # ... (다른 모든 효과 물약의 _lingering 버전 추가, 단, _splash 버전이 있어야 함) ...
    "potion_of_harming_lingering": {"id": "potion_of_harming_lingering", "name": "잔류형 고통의 물약", "description": "잔류형: 즉시 피해 구름", "image": "potions/images/potion_of_harming.gif", "type": "potion_lingering"},

    # === 재료 아이템 ===
    "nether_wart": {"id": "nether_wart", "name": "네더 사마귀", "description": "어색한 물약의 재료.",
                    "image": "potions/images/nether_wart.png", "type": "ingredient",
                    "full_description": "어색한 물약의 베이스 재료.\n획득처: 네더 요새의 영혼 모래밭에서 재배하거나 상자에서 발견."},
    "redstone_dust": {"id": "redstone_dust", "name": "레드스톤 가루", "description": "물약 지속시간 연장 / 평범한 물약 재료.",
                      "image": "potions/images/redstone_dust.png", "type": "ingredient",
                      "full_description": "물약의 지속 시간을 연장시킵니다.\n획득처: 레드스톤 광석을 채광하거나 마녀 처치."},
    "glowstone_dust": {"id": "glowstone_dust", "name": "발광석 가루", "description": "물약 효과 강화 / 진한 물약 재료.",
                       "image": "potions/images/glowstone_dust.png", "type": "ingredient",
                       "full_description": "물약의 효과 레벨을 강화(I -> II)시킵니다.\n획득처: 네더의 발광석 블록을 부수어 획득."},
    "fermented_spider_eye": {"id": "fermented_spider_eye", "name": "발효된 거미 눈", "description": "물약 효과 반전 또는 나약함의 물약 재료.",
                             "image": "potions/images/fermented_spider_eye.png", "type": "ingredient",
                             "full_description": "조합: 거미 눈 + 설탕 + 버섯\n물약의 효과를 반전시키거나 나약함 물약을 만듭니다.\n(예: 신속 -> 감속, 치유 -> 고통)"},
    "gunpowder": {"id": "gunpowder", "name": "화약", "description": "투척용 물약으로 변환.",
                  "image": "potions/images/gunpowder.png", "type": "ingredient",
                  "full_description": "일반 물약을 투척용 물약으로 변환합니다.\n획득처: 크리퍼, 가스트, 블레이즈 처치."},
    "dragon_breath": {"id": "dragon_breath", "name": "드래곤의 숨결", "description": "잔류형 물약으로 변환.",
                      "image": "potions/images/dragon_breath.png", "type": "ingredient",
                      "full_description": "투척용 물약을 잔류형 물약으로 변환합니다.\n특수 획득처: 엔더 드래곤이 내뿜는 보라색 숨결을 유리병으로 수집."},
    "sugar": {"id": "sugar", "name": "설탕", "description": "신속 효과 재료.", "image": "potions/images/sugar.png",
              "type": "ingredient", "full_description": "신속 물약 재료.\n획득처: 사탕수수 조합."},
    "rabbit_foot": {"id": "rabbit_foot", "name": "토끼 발", "description": "도약 효과 재료.",
                    "image": "potions/images/rabbit_foot.png", "type": "ingredient",
                    "full_description": "도약 물약 재료.\n획득처: 토끼 처치 (낮은 확률). 행운 III 효과가 있는 토끼에게서 얻기 쉬움."},
    "glistering_melon_slice": {"id": "glistering_melon_slice", "name": "반짝이는 수박 조각", "description": "치유 효과 재료.",
                               "image": "potions/images/glistering_melon_slice.png", "type": "ingredient",
                               "full_description": "조합: 수박 조각 + 금 조각 8개\n치유 물약 재료."},
    "spider_eye": {"id": "spider_eye", "name": "거미 눈", "description": "독 효과 재료.",
                   "image": "potions/images/spider_eye.png", "type": "ingredient",
                   "full_description": "독 물약 재료.\n획득처: 거미, 마녀, 동굴 거미 처치."},
    "pufferfish": {"id": "pufferfish", "name": "복어", "description": "수중 호흡 효과 재료.",
                   "image": "potions/images/pufferfish.png", "type": "ingredient",
                   "full_description": "수중 호흡 물약 재료.\n획득처: 낚시."},
    "magma_cream": {"id": "magma_cream", "name": "마그마 크림", "description": "화염 저항 효과 재료.",
                    "image": "potions/images/magma_cream.png", "type": "ingredient",
                    "full_description": "조합: 슬라임 볼 + 블레이즈 가루\n화염 저항 물약 재료.\n획득처: 마그마 슬라임 처치."},
    "golden_carrot": {"id": "golden_carrot", "name": "황금 당근", "description": "야간 투시 효과 재료.",
                      "image": "potions/images/golden_carrot.png", "type": "ingredient",
                      "full_description": "조합: 당근 + 금 조각 8개\n야간 투시 물약 재료."},
    "blaze_powder": {"id": "blaze_powder", "name": "블레이즈 가루", "description": "힘 효과 재료.",
                     "image": "potions/images/blaze_powder.png", "type": "ingredient",
                     "full_description": "조합: 블레이즈 막대\n힘 물약 재료. 양조기의 연료로도 사용됩니다.\n획득처: 블레이즈 처치."},
    "ghast_tear": {"id": "ghast_tear", "name": "가스트의 눈물", "description": "재생 효과 재료.",
                   "image": "potions/images/ghast_tear.png", "type": "ingredient",
                   "full_description": "재생 물약 재료.\n획득처: 가스트 처치 (낮은 확률)."},
    "turtle_shell": {"id": "turtle_shell", "name": "거북 등딱지", "description": "거북 도사 효과 재료.",
                     "image": "potions/images/turtle_shell.png", "type": "ingredient",
                     "full_description": "조합: 인후(Scute) 5개\n거북 도사의 물약 재료.\n획득처: 새끼 거북이가 자라면서 떨어뜨림."},
    "phantom_membrane": {"id": "phantom_membrane", "name": "팬텀 막", "description": "느린 낙하 효과 재료.",
                         "image": "potions/images/phantom_membrane.png", "type": "ingredient",
                         "full_description": "느린 낙하 물약 재료.\n획득처: 팬텀 처치 (잠을 오랫동안 안 잘 경우 나타남)."},
}
# --- 데이터 정의 끝 ---

INGREDIENTS_DATA = {k: v for k, v in ITEMS.items() if v['type'] == 'ingredient'}
ALL_POTIONS_DATA = {k: v for k, v in ITEMS.items() if v['type'] not in ['ingredient']}

RECIPES = {
    # 1. 기초 및 변환 재료 (물병에 추가 시)
    ("water_bottle", "nether_wart"): "awkward_potion",
    ("water_bottle", "redstone_dust"): "mundane_potion",
    ("water_bottle", "glowstone_dust"): "thick_potion",
    ("water_bottle", "fermented_spider_eye"): "potion_of_weakness_base",

    # 2. 효과 물약 (주로 어색한 물약 + 효과 재료)
    ("awkward_potion", "sugar"): "potion_of_swiftness",
    ("awkward_potion", "rabbit_foot"): "potion_of_leaping",
    ("awkward_potion", "glistering_melon_slice"): "potion_of_healing",
    ("awkward_potion", "spider_eye"): "potion_of_poison",
    ("awkward_potion", "pufferfish"): "potion_of_water_breathing",
    ("awkward_potion", "magma_cream"): "potion_of_fire_resistance",
    ("awkward_potion", "golden_carrot"): "potion_of_night_vision",
    ("awkward_potion", "blaze_powder"): "potion_of_strength",
    ("awkward_potion", "ghast_tear"): "potion_of_regeneration",
    ("awkward_potion", "turtle_shell"): "potion_of_the_turtle_master",
    ("awkward_potion", "phantom_membrane"): "potion_of_slow_falling",

    # 3. 효과 물약 - 기간 연장 (기존 물약 + 레드스톤 가루)
    ("potion_of_fire_resistance", "redstone_dust"): "potion_of_fire_resistance_long",
    ("potion_of_regeneration", "redstone_dust"): "potion_of_regeneration_long",
    ("potion_of_strength", "redstone_dust"): "potion_of_strength_long",
    ("potion_of_swiftness", "redstone_dust"): "potion_of_swiftness_long",
    ("potion_of_night_vision", "redstone_dust"): "potion_of_night_vision_long",
    ("potion_of_invisibility", "redstone_dust"): "potion_of_invisibility_long",
    ("potion_of_water_breathing", "redstone_dust"): "potion_of_water_breathing_long",
    ("potion_of_leaping", "redstone_dust"): "potion_of_leaping_long",
    ("potion_of_slow_falling", "redstone_dust"): "potion_of_slow_falling_long",
    ("potion_of_poison", "redstone_dust"): "potion_of_poison_long",
    ("potion_of_weakness_base", "redstone_dust"): "potion_of_weakness_long",  # 물병 기반 나약함에 레드스톤
    ("potion_of_slowness", "redstone_dust"): "potion_of_slowness_long",
    ("potion_of_the_turtle_master", "redstone_dust"): "potion_of_the_turtle_master_long",

    # 4. 효과 물약 - 강화 (기존 물약 + 발광석 가루)
    ("potion_of_healing", "glowstone_dust"): "potion_of_healing_strong",
    ("potion_of_regeneration", "glowstone_dust"): "potion_of_regeneration_strong",
    ("potion_of_strength", "glowstone_dust"): "potion_of_strength_strong",
    ("potion_of_swiftness", "glowstone_dust"): "potion_of_swiftness_strong",
    ("potion_of_leaping", "glowstone_dust"): "potion_of_leaping_strong",
    ("potion_of_poison", "glowstone_dust"): "potion_of_poison_strong",
    ("potion_of_harming", "glowstone_dust"): "potion_of_harming_strong",
    ("potion_of_slowness_long", "glowstone_dust"): "potion_of_slowness_strong",  # 감속IV는 감속(지속)에 발광석 (실제마크에서 복잡)
    ("potion_of_the_turtle_master", "glowstone_dust"): "potion_of_the_turtle_master_strong",

    # 5. 효과 물약 - 부패/변형 (기존 물약 + 발효된 거미 눈)
    ("potion_of_swiftness", "fermented_spider_eye"): "potion_of_slowness",
    ("potion_of_leaping", "fermented_spider_eye"): "potion_of_slowness",
    ("potion_of_healing", "fermented_spider_eye"): "potion_of_harming",
    ("potion_of_poison", "fermented_spider_eye"): "potion_of_harming",
    ("potion_of_night_vision", "fermented_spider_eye"): "potion_of_invisibility",
    ("potion_of_strength", "fermented_spider_eye"): "potion_of_weakness_from_effect",
    ("potion_of_regeneration", "fermented_spider_eye"): "potion_of_weakness_from_effect",

    # 6. 투척용으로 변환 (기존 물약 + 화약) - 주요 물약만 예시, 모든 'potion' 타입에 적용 가능
    ("potion_of_swiftness", "gunpowder"): "potion_of_swiftness_splash",
    ("potion_of_healing", "gunpowder"): "potion_of_healing_splash",
    ("potion_of_poison", "gunpowder"): "potion_of_poison_splash",
    ("potion_of_harming", "gunpowder"): "potion_of_harming_splash",
    # ... (다른 potion 타입 + gunpowder -> _splash)

    # 7. 잔류형으로 변환 (투척용 물약 + 드래곤의 숨결) - 주요 물약만 예시
    ("potion_of_swiftness_splash", "dragon_breath"): "potion_of_swiftness_lingering",
    ("potion_of_healing_splash", "dragon_breath"): "potion_of_healing_lingering",
    ("potion_of_harming_splash", "dragon_breath"): "potion_of_harming_lingering",
    # ... (다른 _splash 타입 + dragon_breath -> _lingering)
}


# --- 데이터 정의 끝 ---


# 특정 물약의 조합법을 찾는 함수
def find_recipe_for_potion(potion_id_to_find):
    for (base_id, ingredient_id), result_id in RECIPES.items():
        if result_id == potion_id_to_find:
            # ITEMS에서 실제 객체 정보를 가져옴
            base_item = ITEMS.get(base_id)
            ingredient_item = ITEMS.get(ingredient_id)
            result_item = ITEMS.get(result_id)

            # 혹시라도 ID는 있는데 ITEMS에 정의 안된 경우 방지
            if base_item and ingredient_item and result_item:
                return {
                    "base": base_item,
                    "ingredient": ingredient_item,
                    "result": result_item
                }
    return None


# --- 뷰 함수 ---
def potion_simulator_view(request):
    current_potion_id = request.session.get('current_potion_id', 'water_bottle')
    applied_ingredients_log = request.session.get('applied_ingredients_log', [])
    recipe_to_display = None
    message = None

    if request.method == "POST":
        action = request.POST.get("action")
        item_id_from_form = request.POST.get("item_id")  # form에서 넘어온 item_id

        if action == "select_potion_from_list":
            if item_id_from_form in ALL_POTIONS_DATA:
                current_potion_id = item_id_from_form
                applied_ingredients_log = []
                message = f"'{ITEMS[current_potion_id]['name']}'(을)를 선택했습니다."
                # 선택한 물약의 레시피를 바로 찾아서 recipe_to_display에 할당
                recipe_to_display = find_recipe_for_potion(current_potion_id)
            else:
                message = "목록에 없는 물약입니다."

        elif action == "add_ingredient":
            if item_id_from_form in INGREDIENTS_DATA:
                ingredient_info = INGREDIENTS_DATA[item_id_from_form]
                current_potion_info_obj = ITEMS.get(current_potion_id)

                if not current_potion_info_obj:
                    message = "현재 물약 상태를 알 수 없습니다. 초기화 후 다시 시도해주세요."
                else:
                    recipe_key = (current_potion_id, item_id_from_form)
                    new_potion_id_candidate = RECIPES.get(recipe_key)

                    if new_potion_id_candidate and new_potion_id_candidate in ITEMS:
                        current_potion_id = new_potion_id_candidate
                        applied_ingredients_log.append({
                            "id": item_id_from_form,  # 실제 사용된 재료의 ID
                            "name": ingredient_info["name"],
                            "description": ingredient_info["description"],
                            "image": ingredient_info["image"]
                        })
                        message = f"'{ingredient_info['name']}' 추가! 결과: '{ITEMS[current_potion_id]['name']}'"
                        # 조합된 새 물약의 레시피를 찾아서 recipe_to_display에 할당
                        recipe_to_display = find_recipe_for_potion(current_potion_id)
                    elif new_potion_id_candidate and new_potion_id_candidate not in ITEMS:
                        message = f"조합 결과물('{new_potion_id_candidate}')에 대한 정의가 ITEMS에 없습니다."
                    else:
                        message = f"'{current_potion_info_obj['name']}'에 '{ingredient_info['name']}'(을)를 사용할 수 없습니다."
            else:
                message = "선택한 아이템은 재료가 아닙니다."

        elif action == "reset_brewing":
            current_potion_id = 'water_bottle'
            applied_ingredients_log = []
            recipe_to_display = None
            message = "조합을 초기화했습니다."

        request.session['current_potion_id'] = current_potion_id
        request.session['applied_ingredients_log'] = applied_ingredients_log

        # POST 요청 후 레시피 표시 로직 유지
        if not recipe_to_display and current_potion_id != 'water_bottle':
            if not message or action != "select_potion_from_list":
                recipe_to_display = find_recipe_for_potion(current_potion_id)

    # GET 요청이거나, POST 처리 후 recipe_to_display가 아직 설정되지 않은 경우 (예: 페이지 첫 로드)
    if not recipe_to_display and current_potion_id != 'water_bottle':
        recipe_to_display = find_recipe_for_potion(current_potion_id)

    # --- 불가능한 재료 ID 목록 계산 ---
    impossible_ingredients_ids = []

    # 모든 재료 ID를 순회하며 현재 물약과 조합이 가능한지 확인
    for ingredient_id in INGREDIENTS_DATA.keys():
        recipe_key = (current_potion_id, ingredient_id)
        if recipe_key not in RECIPES:
            # RECIPES 딕셔너리에 해당 조합이 없으면 불가능한 재료로 간주
            # (단, water_bottle의 경우 nether_wart를 제외한 다른 재료도 초반에 빨간색으로 표시되지 않도록 하려면 복잡한 예외 처리 필요)
            # 여기서는 RECIPES에 없으면 모두 불가능하다고 간단히 가정합니다.
            impossible_ingredients_ids.append(ingredient_id)

    current_potion_display_info = ITEMS.get(current_potion_id,
                                            {"name": "알 수 없음", "description": "정보 없음", "image": None})

    context = {
        'all_ingredients': INGREDIENTS_DATA,
        'all_potions_for_list': ALL_POTIONS_DATA,
        'current_potion_id': current_potion_id,
        'current_potion_name': current_potion_display_info['name'],
        'current_potion_description': current_potion_display_info['description'],
        'current_potion_image': current_potion_display_info.get('image'),
        'applied_ingredients_log': applied_ingredients_log,
        'recipe_to_display': recipe_to_display,
        'message': message,
        # 새로 추가된 컨텍스트 변수
        'impossible_ingredients_ids': impossible_ingredients_ids,
    }
    return render(request, "potions/simulator.html", context)