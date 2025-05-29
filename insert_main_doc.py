from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]
wiki = db["wiki"]

wiki.delete_many({})

wiki.insert_one({
    "title": "대문",
    "content": "# 스티븐 위키에 오신 것을 환영합니다!\n이 문서는 대문입니다.",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "last_editor": "admin",
    "history": [
        {
            "editor": "admin",
            "timestamp": datetime.utcnow(),
            "summary": "초기 생성",
            "content": "# 스티븐 위키에 오신 것을 환영합니다!\n이 문서는 대문입니다."
        }
    ]
})

print("✅ 대문 문서 삽입 완료")

