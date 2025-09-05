from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

signer = TimestampSigner(salt="accounts.email.verify")

def make_email_verify_token(user):
    return signer.sign(f"{user.pk}:{user.email}")

def read_email_verify_token(token, max_age=60*60*24):  # 24h
    try:
        raw = signer.unsign(token, max_age=max_age)
        uid, email = raw.split(":", 1)
        return int(uid), email
    except (BadSignature, SignatureExpired, ValueError):
        return None, None
