from django.shortcuts import render, redirect, get_object_or_404
from pymongo import MongoClient
from datetime import datetime
from .models import WikiPage

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]
wiki = db["wiki"]


# MongoDB 기반 문서 보기
def wiki_detail_view(request, title):
    doc = wiki.find_one({"title": title})
    if doc:
        return render(request, "wiki/detail.html", {
            "title": doc["title"],
            "content": doc["content"]
        })
    else:
        return render(request, "wiki/not_found.html", {"title": title})


# MongoDB 기반 문서 편집
def wiki_edit_view(request, title):
    doc = wiki.find_one({"title": title})

    if request.method == "POST":
        new_content = request.POST.get("content", "")
        summary = request.POST.get("summary", "")
        now = datetime.utcnow()

        wiki.update_one(
            {"title": title},
            {
                "$set": {
                    "content": new_content,
                    "updated_at": now,
                    "last_editor": "admin"
                },
                "$push": {
                    "history": {
                        "editor": "admin",
                        "timestamp": now,
                        "summary": summary,
                        "content": new_content
                    }
                }
            },
            upsert=True
        )
        return redirect("wiki:wiki_detail", title=title)

    return render(request, "wiki/edit.html", {
        "title": title,
        "content": doc["content"] if doc else "",
    })


# 문서 내용 일부만 렌더 (부분 갱신 용도)
def wiki_detail_partial(request, title):
    doc = wiki.find_one({"title": title})
    if doc:
        return render(request, "wiki/detail_partial.html", {
            "title": doc["title"],
            "content": doc["content"]
        })
    else:
        return render(request, "wiki/not_found.html", {"title": title})


# (선택) Django ORM 기반 문서 뷰 - 예전 호환용
def view_page(request, title):
    page = get_object_or_404(WikiPage, title=title)
    return render(request, 'wiki/view.html', {'page': page})


# (선택) Django ORM 기반 문서 편집
def edit_page(request, title):
    page, _ = WikiPage.objects.get_or_create(title=title)
    if request.method == 'POST':
        page.content = request.POST.get('content', '')
        page.save()
        return redirect('wiki:view', title=title)
    return render(request, 'wiki/edit.html', {'page': page})
