
from django.shortcuts import render, redirect
from django.conf import settings

# --- 인증 관련 기능 ---
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# --- 이메일 및 템플릿 관련 기능 ---
from django.core.mail import send_mail
from django.template.loader import render_to_string # 🚨 이 줄을 추가 또는 확인!

# --- HTTP 응답 관련 기능 ---
from django.http import JsonResponse # 🚨 이 줄을 추가 또는 확인!

# --- Python 내장 모듈 ---
import random
import string
import json

# 1. 로그인 함수
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main:home") # main 앱의 home으로 이동
        else:
            messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    return render(request, "accounts/login.html")

# 2. 회원가입 함수
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        email = request.POST.get("email")

        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, "accounts/register.html", {'username': username, 'email': email})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 아이디입니다.')
            return render(request, "accounts/register.html", {'email': email})

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect("home")
    
    return render(request, "accounts/register.html")

# 3. 로그아웃 함수
def logout_view(request):
    logout(request)
    return redirect("accounts:login") # 로그인 페이지로 이동

def generate_otp(length=6):
    """6자리 숫자 OTP를 생성합니다."""
    return "".join(random.choices(string.digits, k=length))

# --- 'OTP 전송' 요청을 처리할 새로운 뷰 ---
def send_otp_view(request):
    if request.method == 'POST':
        try:
            # JavaScript가 보낸 JSON 데이터 파싱
            data = json.loads(request.body)
            email_to = data.get('email')

            if not email_to:
                return JsonResponse({'success': False, 'message': '이메일 주소를 입력해주세요.'}, status=400)
            
            # OTP 생성
            otp_code = generate_otp()
            
            # 🚨 중요: 생성된 OTP를 세션에 저장하여 나중에 검증할 수 있도록 함
            request.session['otp_code'] = otp_code
            request.session['otp_email'] = email_to
            
            print(f"Generated OTP for {email_to}: {otp_code}") # 터미널에 OTP 출력 (확인용)

            # 이메일 본문을 otp_email.html 템플릿을 이용해 생성
            html_message = render_to_string('accounts/otp_email.html', {'otp_code': otp_code})

            # 이메일 발송
            send_mail(
                subject='[스티븐 위키] 회원가입 인증번호입니다.',
                message='', # HTML 이메일을 보낼 것이므로 일반 텍스트는 비워둠
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_to],
                html_message=html_message,
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': f"'{email_to}'(으)로 인증번호를 성공적으로 발송했습니다."})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
        except Exception as e:
            print(f"Error sending email: {e}")
            return JsonResponse({'success': False, 'message': '이메일 발송 중 오류가 발생했습니다.'}, status=500)

    return JsonResponse({'success': False, 'message': '잘못된 접근 방식입니다.'}, status=405)    

