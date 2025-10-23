import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from pymongo import MongoClient


SAMPLE_DOCS = {
    '청금석': (
        '# 청금석\n\n'
        '청금석은 [[동굴]]에서 생성되는 "광맥" 형태의 자원입니다.\n\n'
        '- 채굴 도구: 철 곡괭이 이상 권장\n'
        '- 용도: 인챈트에 필요한 라필라즈리로 사용\n'
        '- 생성: 주로 Y=-32 ~ 32 구간\n'
    ),
    '동굴': (
        '# 동굴\n\n'
        '동굴은 지하 공간으로, 각종 광물의 "광맥"이 분포합니다.\n\n'
        '- 몬스터 스폰에 유의\n'
        '- 횃불로 경로 표시\n'
    ),
    '광맥': (
        '# 광맥\n\n'
        '광물 "블록"들이 뭉쳐 있는 집합입니다. 예: 석탄, 철, 청금석 등.\n\n'
        '- 채굴 시 행운 인챈트 효과 적용\n'
        '- 광맥 크기는 자원마다 상이\n'
    ),
    '튜토리얼': (
        '# 튜토리얼\n\n'
        '마인크래프트의 기본 조작과 생존 팁을 소개합니다.\n\n'
        '- 나무 캐기 → 작업대 → 기본 도구 제작\n'
        '- 첫날밤을 대비해 임시 거처 마련\n'
        '- 굶주림 방지를 위한 음식 확보\n\n'
        '추가로 `/wiki/게임_시작하기` 문서를 참고하세요.\n'
    ),
    '게임_시작하기': (
        '# 게임 시작하기\n\n'
        '월드를 생성하고 기본 설정을 조정하는 방법을 안내합니다.\n\n'
        '1. 난이도와 게임 모드 선택\n\n'
        '2. 스폰 지형 파악과 리스폰 포인트 설정\n'
    ),
    '인챈트': (
        '# 인챈트\n\n'
        '인챈트 테이블, 모루, 라필라즈리를 활용한 장비 강화 가이드입니다.\n\n'
        '- 효율, 내구성, 날카로움 등 주요 인챈트 소개\n'
        '- /enchant-recommender/ 에서 추천 조합 확인\n'
    ),
    '양조': (
        '# 양조\n\n'
        '포션 재료와 양조 스탠드를 활용해 다양한 포션을 만드는 법을 다룹니다.\n\n'
        '- 화약, 레드스톤, 발광석으로 지속시간/효과 조정\n'
        '- 주요 포션 레시피 요약\n'
    ),
}


class Command(BaseCommand):
    help = 'Import built-in sample wiki pages into MongoDB.'

    def add_arguments(self, parser):
        parser.add_argument('--mongo', type=str, default='mongodb://localhost:27017', help='Mongo URI')
        parser.add_argument('--db', type=str, default='minecraft', help='Mongo database name')
        parser.add_argument('--collection', type=str, default='wiki', help='Mongo collection name')
        parser.add_argument('--reset', action='store_true', help='Drop collection before import')

    def handle(self, *args, **options):
        client = MongoClient(options['mongo'])
        db = client[options['db']]
        col = db[options['collection']]

        if options['reset']:
            col.drop()

        col.create_index('title', unique=True)

        imported = 0
        for title, content in SAMPLE_DOCS.items():
            col.update_one({ 'title': title }, { '$set': { 'title': title, 'content': content } }, upsert=True)
            imported += 1

        self.stdout.write(self.style.SUCCESS(f'Imported/updated {imported} sample documents.'))

