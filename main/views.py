from django.shortcuts import render
from pymongo import MongoClient

def home_view(request):
    client = MongoClient("mongodb://localhost:27017")
    db = client["minecraft"]
    wiki_collection = db["wiki"]

    main_doc = wiki_collection.find_one({"title": "대문"})  # "대문"이라는 제목을 가진 문서

    return render(request, "main/home.html", {"main_doc": main_doc})
