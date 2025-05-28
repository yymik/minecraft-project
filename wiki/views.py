from django.shortcuts import render, redirect, get_object_or_404
from .models import WikiPage
from pymongo import MongoClient
from datetime import datetime


def home(request):
    pages = WikiPage.objects.all()
    return render(request, 'wiki/home.html', {'pages': pages})

def view_page(request, title):
    page = get_object_or_404(WikiPage, title=title)
    return render(request, 'wiki/view.html', {'page': page})

def edit_page(request, title):
    page, _ = WikiPage.objects.get_or_create(title=title)
    if request.method == 'POST':
        page.content = request.POST.get('content', '')
        page.save()
        return redirect('wiki:view', title=title)
    return render(request, 'wiki/edit.html', {'page': page})

from django.shortcuts import render, redirect
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["minecraft"]
wiki = db["wiki"]

def wiki_detail_view(request, title):
    client = MongoClient("mongodb://localhost:27017")
    db = client["minecraft"]
    doc = db["wiki"].find_one({"title": title})
    if doc:
        return render(request, "wiki/detail.html", {
            "title": doc["title"],
            "content": doc["content"]
        })
    else:
        return render(request, "wiki/not_found.html", {"title": title})


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
            }
        )
        return redirect("wiki_detail", title=title)
    
    return render(request, "wiki/edit.html", {
        "title": title,
        "content": doc["content"] if doc else "",
    })
