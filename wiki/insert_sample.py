from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]  # 프로젝트에서 사용 중인 DB 이름
wiki_collection = db["wiki"]

document = {
    "title": "튜토리얼",
    "content": "# 튜토리얼\n이 문서는 스티븐 위키의 사용법을 설명합니다.",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "last_editor": "admin",
    "history": [
        {
            "editor": "admin",
            "timestamp": datetime.utcnow(),
            "summary": "초기 생성",
            "content": "# 튜토리얼\n이 문서는 스티븐 위키의 사용법을 설명합니다."
        }
    ]
}

wiki_collection.insert_one(document)
print("튜토리얼 문서 삽입 완료")