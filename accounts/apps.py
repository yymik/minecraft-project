<<<<<<< HEAD
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
=======
import os
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import random
import string

# --- Flask 앱 기본 설정 ---
app = Flask(__name__)

# --- 🚨 이메일 서버 설정 (가장 중요!) 🚨 ---
# Gmail을 사용하는 경우의 예시입니다.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# 1. 보내는 사람의 Gmail 주소를 입력하세요.
#    환경 변수를 사용하는 것이 안전하지만, 테스트를 위해 직접 입력합니다.
app.config['MAIL_USERNAME'] = 'minanyang10@gamil.com' 

# 2. Gmail '앱 비밀번호'를 입력하세요. (계정 비밀번호가 아닙니다!)
#    (아래 'Gmail 앱 비밀번호 생성 방법' 참고)
app.config['MAIL_PASSWORD'] = '1AA-2506-0177206 '

mail = Mail(app)

# --- OTP 생성 함수 ---
def generate_otp(length=6):
    """6자리 숫자 OTP를 생성합니다."""
    return "".join(random.choices(string.digits, k=length))

# --- URL 라우트 정의 ---

# 1. 메인 회원가입 페이지를 보여주는 라우트
@app.route('/')
def register_page():
    return render_template('register.html')

# 2. 'OTP 전송' 버튼을 눌렀을 때 요청을 처리하는 라우트
@app.route('/send-otp', methods=['POST'])
def send_otp():
    # 클라이언트(JavaScript)가 보낸 데이터 받기
    data = request.get_json()
    email_to = data.get('email')

    if not email_to:
        return jsonify({'success': False, 'message': '이메일 주소를 입력해주세요.'}), 400

    # OTP 생성
    otp_code = generate_otp()
    
    # 여기에서 생성된 OTP를 세션이나 임시 저장소에 저장해야 하지만,
    # 지금은 이메일 발송 기능에만 집중합니다.
    print(f"Generated OTP for {email_to}: {otp_code}") # 터미널에 OTP 출력 (확인용)

    try:
        # 이메일 객체 생성
        msg = Message(
            subject="[스티븐 위키] 회원가입 인증번호입니다.",
            sender=('스티븐 위키', app.config['MAIL_USERNAME']), # 보내는 사람 이름과 이메일
            recipients=[email_to] # 사용자가 입력한 이메일 주소
        )
        
        # otp_email.html 템플릿을 사용하여 이메일 본문 생성
        msg.html = render_template('otp_email.html', otp_code=otp_code)
        
        # 이메일 발송!
        mail.send(msg)

        # 성공 응답을 클라이언트로 보냄
        return jsonify({'success': True, 'message': f"'{email_to}'(으)로 인증번호를 성공적으로 발송했습니다."})

    except Exception as e:
        # 이메일 발송 실패 시
        print(f"Error sending email to {email_to}: {e}") # 터미널에 전체 오류 출력
        return jsonify({'success': False, 'message': '이메일 발송에 실패했습니다. 관리자 설정을 확인해주세요.'}), 500

# --- 앱 실행 ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)
>>>>>>> 1756a89 (0608 15:51 json 스킨편집기)
