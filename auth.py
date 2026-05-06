# mdumeni-backend/auth.py
import os, hashlib, hmac, json, base64, time

def _secret() -> str:
    """Read JWT_SECRET fresh each call — avoids module-load timing issues."""
    return os.environ.get("JWT_SECRET", "mdumeni-dev-secret-change-in-production")

def hash_pin(pin: str, phone: str) -> str:
    return hashlib.sha256(f"{phone}:{pin}:mdumeni-salt".encode()).hexdigest()

def verify_pin(pin: str, phone: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_pin(pin, phone), stored_hash)

def create_token(farmer_id: str, phone: str) -> str:
    secret = _secret()
    header = base64.urlsafe_b64encode(
        json.dumps({"alg":"HS256","typ":"JWT"}, separators=(',',':')).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({
            "farmer_id": farmer_id,
            "phone":     phone,
            "iat":       int(time.time()),
            "exp":       int(time.time()) + (90 * 24 * 3600),
        }, separators=(',',':')).encode()
    ).rstrip(b"=").decode()
    sig = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{header}.{payload}.{sig}"

def verify_token(token: str) -> dict | None:
    secret = _secret()
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        expected = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        if not hmac.compare_digest(expected, signature):
            return None
        padded = payload + "=" * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None

def normalize_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("07") or phone.startswith("08"):
        phone = "+263" + phone[1:]
    elif phone.startswith("263") and not phone.startswith("+"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+263" + phone
    return phone


    @app.get("/debug/secret", tags=["System"])
    def debug_secret():
        import os
        secret = os.environ.get("JWT_SECRET", "NOT SET")
        return {"secret_length": len(secret), "secret_prefix": secret[:8]}