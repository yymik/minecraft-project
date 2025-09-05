
from pathlib import Path

# BASE_DIR: 프로젝트 최상위 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 보안 관련 설정
SECRET_KEY = 'django-insecure-*@3*4nz0i6-5&0cz25eg6s7d6nq@m^1tpue3@ek7)%t@gqf-+u'
DEBUG = True
ALLOWED_HOSTS = []

# 설치된 앱 목록
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'chatbot',
    'main',
    'potions',
    'enchant_recommender',
    'wiki',
    'django_extensions',
    'skin_editor',
    'save_analyzer',
]

# 미들웨어 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL 설정 루트
ROOT_URLCONF = 'config.urls'

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'wiki' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI 애플리케이션 설정
WSGI_APPLICATION = 'config.wsgi.application'

# 데이터베이스 설정 (SQLite 사용)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 비밀번호 유효성 검사
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 언어/시간대 설정
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 정적 파일 경로 설정
STATIC_URL = 'static/'

# 기본 자동 필드 타입 설정
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF 및 보안 설정
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# --- 이메일 설정 ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP 서버 주소
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'minanyang10@gmail.com'      # 🚨 실제 본인의 Gmail 주소로 변경
EMAIL_HOST_PASSWORD = 'hffl kpkf nfh rcisc'     # 🚨 실제 본인의 Gmail 앱 비밀번호로 변경
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SITE_URL = "http://localhost:8000"  # 배포 시 실제 도메인으로
