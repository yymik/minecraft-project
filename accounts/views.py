import json, random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.core.cache import cache

try:
    from ratelimit.decorators import ratelimit
except Exception:
    def ratelimit(*args, **kwargs):
        def deco(fn): return fn
        return deco

from .models import EmailVerificationToken, UserProfile
from .tokens import make_email_verify_token, read_email_verify_token

UserModel = get_user_model()
pr_token_gen = PasswordResetTokenGenerator()

OTP_TTL = 60 * 10  # 10분

def _abs_url(request, path):
    base = getattr(settings, "SITE_URL", request.build_absolute_uri("/").rstrip("/"))
    return path if str(path).startswith("http") else f"{base}{path}"

def _gen_otp():
    return f"{random.randint(0, 999999):06d}"

def _norm_email(email: str) -> str:
    return (email or "").strip().lower()

# ====== 로그인/로그아웃 ======
@require_http_methods(["GET", "POST"])
@ratelimit(key="ip", rate="20/m", block=True)
def login_view(request):
    if request.method == "GET":
        # 비번 재설정 안내가 리다이렉트로 온 경우에도 확실히 보여주기
        if request.GET.get("reset_sent") == "1":
            messages.info(request, "재설정 링크를 이메일로 전송했습니다. 메일함(스팸함 포함)을 확인하세요.")
        return render(request, "accounts/login.html")
    
    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    
    # 디버깅을 위한 로그
    print(f"Login attempt: username='{username}', password_length={len(password)}")
    
    # 사용자 존재 확인
    try:
        user_obj = UserModel.objects.get(username=username)
        print(f"User found: {user_obj.username}, is_active: {user_obj.is_active}")
    except UserModel.DoesNotExist:
        print(f"User '{username}' not found")
        messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
        return render(request, "accounts/login.html")
    
    user = authenticate(request, username=username, password=password)
    if not user:
        print(f"Authentication failed for user '{username}'")
        messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
        return render(request, "accounts/login.html")
    
    if not user.is_active:
        print(f"User '{username}' is not active")
        messages.error(request, "이메일 인증이 필요합니다. 가입 시 받은 메일을 확인하세요.")
        return render(request, "accounts/login.html")
    
    print(f"Login successful for user '{username}'")
    login(request, user)
    return redirect("main:home")

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("main:home")

# ====== 회원가입 + 인증메일 발송 ======
@require_http_methods(["GET", "POST"])
@ratelimit(key="ip", rate="10/m", block=True)
def register_view(request):
    if request.method == "GET":
        return render(request, "accounts/register.html")

    username = request.POST.get("username", "").strip()
    email = _norm_email(request.POST.get("email"))
    minecraft_uuid = request.POST.get("minecraft_uuid", "").strip()
    password = request.POST.get("password", "")
    password2 = request.POST.get("password2", "")

    if not username or not email or not minecraft_uuid or not password:
        messages.error(request, "필수 항목이 비었습니다.")
        return render(request, "accounts/register.html")
    if password != password2:
        messages.error(request, "비밀번호가 일치하지 않습니다.")
        return render(request, "accounts/register.html")
    if UserModel.objects.filter(username=username).exists():
        messages.error(request, "이미 사용 중인 아이디입니다.")
        return render(request, "accounts/register.html")
    if UserModel.objects.filter(email=email).exists():
        messages.error(request, "이미 사용 중인 이메일입니다.")
        return render(request, "accounts/register.html")
    
    # UUID 중복 검사
    normalized_uuid = minecraft_uuid.replace('-', '')
    if UserProfile.objects.filter(minecraft_uuid__in=[minecraft_uuid, normalized_uuid]).exists():
        messages.error(request, "이미 사용 중인 Minecraft UUID입니다.")
        return render(request, "accounts/register.html")

    # OTP 선검증을 사용하는 템플릿이면 최종 확인(없으면 건너뜀)
    otp = (request.POST.get("otp") or "").strip()
    saved_otp = cache.get(f"otp:{email}")
    if saved_otp is not None:  # OTP를 발급한 상태라면
        if otp != saved_otp:
            messages.error(request, "이메일 인증코드가 유효하지 않습니다.")
            return render(request, "accounts/register.html")
        cache.delete(f"otp:{email}")

    with transaction.atomic():
        user = UserModel.create_user(
            username=username, email=email, password=password, is_active=True
        ) if hasattr(UserModel, "create_user") else UserModel.objects.create_user(
            username=username, email=email, password=password, is_active=True
        )
        
        # UserProfile 생성 (Minecraft UUID 포함)
        UserProfile.objects.create(user=user, minecraft_uuid=normalized_uuid)
        
        token = make_email_verify_token(user)
        EmailVerificationToken.objects.create(user=user, token=token, purpose="verify_email")

    verify_link = _abs_url(request, reverse("accounts:verify") + f"?token={token}")
    html = render_to_string("accounts/otp_email.html", {
        "user": user,
        "verify_link": verify_link,
    })
    subject = "[이메일 인증] 계정 활성화를 완료해주세요"
    try:
        send_mail(subject, verify_link, settings.DEFAULT_FROM_EMAIL, [email], html_message=html, fail_silently=False)
    except Exception as exc:
        # 이메일 전송 실패 시에도 가입은 진행되도록 하고 안내 메시지 제공
        messages.warning(request, "인증 메일을 보내지 못했습니다. 관리자에게 문의하거나 나중에 다시 시도해주세요.")
        print(f"Email send failed for {email}: {exc}")

    # ✅ 가입 완료 안내 전용 화면으로 리다이렉트
    return redirect("accounts:register_complete", email=email, username=username)

# ====== 회원가입 완료 페이지 ======
@require_http_methods(["GET"])
def register_complete_view(request, email, username):
    return render(request, "accounts/register_complete.html", {
        "email": email, 
        "username": username
    })

# ====== 이메일 인증 처리 ======
@require_http_methods(["GET"])
@ratelimit(key="ip", rate="30/h", block=True)
def verify_email_view(request):
    token = request.GET.get("token")
    if not token:
        messages.error(request, "토큰이 없습니다.")
        return redirect("accounts:login")

    uid, email = read_email_verify_token(token)
    if not uid:
        messages.error(request, "토큰이 유효하지 않거나 만료되었습니다.")
        return redirect("accounts:login")

    try:
        rec = EmailVerificationToken.objects.select_related("user").get(
            token=token, purpose="verify_email", used=False
        )
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "이미 사용되었거나 잘못된 토큰입니다.")
        return redirect("accounts:login")

    user = rec.user
    if user.pk != uid or _norm_email(user.email) != _norm_email(email):
        messages.error(request, "토큰 정보가 일치하지 않습니다.")
        return redirect("accounts:login")

    user.is_active = True
    user.save(update_fields=["is_active"])
    rec.used = True
    rec.save(update_fields=["used"])

    messages.success(request, "이메일 인증이 완료되었습니다. 로그인해주세요.")
    return redirect("accounts:login")

# ====== OTP 전송/검증 (register.html의 {% url 'accounts:send_otp' %} 등 대비) ======
@require_POST
@ratelimit(key="ip", rate="10/m", block=True)
def send_otp_view(request):
    # 항상 OTP 발송(가입 여부와 무관). 정보 노출 방지는 메시지 동일 처리로 해결.
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"success": False, "message": "요청 형식이 올바르지 않습니다."}, status=400)

    email = _norm_email(data.get("email"))
    if not email or "@" not in email:
        return JsonResponse({"success": False, "message": "유효한 이메일을 입력하세요."}, status=400)

    otp = _gen_otp()
    cache.set(f"otp:{email}", otp, OTP_TTL)

    dummy_user = type("U", (), {"username": email.split("@")[0]})()
    html = render_to_string("accounts/otp_email.html", {
        "user": dummy_user,
        "otp_code": otp,  # 메일 템플릿이 코드 출력
    })
    send_mail("[이메일 인증] OTP 코드", f"인증코드: {otp}",
              settings.DEFAULT_FROM_EMAIL, [email], html_message=html)
    return JsonResponse({"success": True, "message": f"{email} 로 인증코드를 전송했습니다."})

@require_POST
@ratelimit(key="ip", rate="20/m", block=True)
def verify_otp_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"success": False, "message": "요청 형식이 올바르지 않습니다."}, status=400)

    email = _norm_email(data.get("email"))
    otp = (data.get("otp") or "").strip()

    if not email or not otp:
        return JsonResponse({"success": False, "message": "이메일/코드를 입력하세요."}, status=400)

    saved = cache.get(f"otp:{email}")
    if not saved:
        return JsonResponse({"success": False, "message": "코드가 만료되었거나 요청되지 않았습니다."}, status=400)
    if otp != saved:
        return JsonResponse({"success": False, "message": "코드가 일치하지 않습니다."}, status=400)

    cache.delete(f"otp:{email}")
    return JsonResponse({"success": True, "message": "인증이 완료되었습니다."})

# ====== 비밀번호 재설정 ======
@require_http_methods(["GET", "POST"])
@ratelimit(key="ip", rate="5/m", block=True)
def forgot_password_view(request):
    if request.method == "GET":
        # ✅ 파일명 통일: accounts/forgot_password.html
        return render(request, "accounts/forgot_password.html")

    email = _norm_email(request.POST.get("email"))
    user = UserModel.objects.filter(email=email, is_active=True).first()
    # 존재 여부와 무관하게 같은 메시지로 처리
    if user:
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = pr_token_gen.make_token(user)
        reset_link = _abs_url(request, reverse("accounts:reset_password",
                                kwargs={"uidb64": uidb64, "token": token}))
        html = render_to_string("accounts/otp_email.html", {
            "user": user,
            "verify_link": reset_link,  # 같은 템플릿 재사용
        })
        send_mail("[비밀번호 재설정] 링크 안내", reset_link,
                  settings.DEFAULT_FROM_EMAIL, [email], html_message=html)

    messages.info(request, "가능한 경우, 비밀번호 재설정 링크를 이메일로 전송했습니다.")
    return redirect(reverse("accounts:login") + "?reset_sent=1")

@require_http_methods(["GET", "POST"])
@ratelimit(key="ip", rate="10/m", block=True)
def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid, is_active=True)
    except Exception:
        messages.error(request, "링크가 유효하지 않습니다.")
        return redirect("accounts:login")

    if not pr_token_gen.check_token(user, token):
        messages.error(request, "토큰이 유효하지 않거나 만료되었습니다.")
        return redirect("accounts:login")

    if request.method == "GET":
        # ✅ 전용 화면
        return render(request, "accounts/reset_password.html")

    new_pw = request.POST.get("new_password") or request.POST.get("password")
    new_pw2 = request.POST.get("new_password2") or request.POST.get("password2")
    if not new_pw or new_pw != new_pw2:
        messages.error(request, "비밀번호가 비었거나 일치하지 않습니다.")
        return render(request, "accounts/reset_password.html")

    user.set_password(new_pw)
    user.save(update_fields=["password"])
    messages.success(request, "비밀번호가 재설정되었습니다. 로그인해주세요.")
    return redirect("accounts:login")

# ====== 마이페이지 ======
@login_required
@require_http_methods(["GET", "POST"])
def mypage_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        new_email = _norm_email(request.POST.get("email"))
        new_uuid_raw = (request.POST.get("minecraft_uuid") or "").strip()
        normalized_uuid = new_uuid_raw.replace("-", "")

        updated_fields = []
        has_error = False

        if new_email and new_email != _norm_email(request.user.email):
            if UserModel.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                messages.error(request, "이미 사용 중인 이메일입니다.")
                has_error = True
            else:
                request.user.email = new_email
                request.user.save(update_fields=["email"])
                updated_fields.append("이메일")

        if new_uuid_raw:
            if len(normalized_uuid) != 32:
                messages.error(request, "Minecraft UUID 형식이 올바르지 않습니다.")
                has_error = True
            elif UserProfile.objects.filter(minecraft_uuid__in=[new_uuid_raw, normalized_uuid]).exclude(pk=profile.pk).exists():
                messages.error(request, "이미 사용 중인 Minecraft UUID입니다.")
                has_error = True
            else:
                profile.minecraft_uuid = new_uuid_raw if len(new_uuid_raw) <= 36 else normalized_uuid
                profile.save(update_fields=["minecraft_uuid"])
                updated_fields.append("Minecraft UUID")
        elif profile.minecraft_uuid:
            profile.minecraft_uuid = ""
            profile.save(update_fields=["minecraft_uuid"])
            updated_fields.append("Minecraft UUID")

        if not has_error:
            if updated_fields:
                messages.success(request, f"{', '.join(updated_fields)} 정보가 업데이트되었습니다.")
            else:
                messages.info(request, "변경된 내용이 없습니다.")

        return redirect("accounts:mypage")

    wiki_pages = []
    try:
        from wiki.models import WikiPage
        wiki_pages = WikiPage.objects.filter(author=request.user).order_by('-created_at')[:10]
    except ImportError:
        pass

    context = {
        'profile': profile,
        'wiki_pages': wiki_pages,
    }

    return render(request, "accounts/mypage.html", context)
