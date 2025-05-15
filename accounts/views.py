from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "accounts/login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect("home")
    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def home_view(request):
    return render(request, 'accounts/home.html')

def chat_view(request):
    user_input = None
    bot_response = None

    if request.method == "POST":
        user_input = request.POST.get("user_input")

        if "청금석" in user_input:
            bot_response = "청금석은 인챈트 필수 재료입니다."
        else:
            bot_response = "죄송해요, 아직 학습되지 않은 질문이에요!"

    return render(request, "accounts/chat.html", {
        "user_input": user_input,
        "bot_response": bot_response
    })