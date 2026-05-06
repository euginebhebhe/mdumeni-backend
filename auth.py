# mdumeni-backend/auth.py
# Farmer identity — phone number + 4-digit PIN
# No SMS needed — farmer remembers their PIN
# Returns a simple JWT token the app stores locally

import os
import hashlib
import hmac
import json
import base64
import time
from datetime import datetime, timezone

# Secret for signing tokens — set in Render env vars
JWT_SECRET = os.environ.get("JWT_SECRET", "mdumeni-2026-intelli-farming")

def hash_pin(pin: str, phone: str) -> str:
    """SHA-256 hash of PIN + phone as salt — not reversible."""
    key = f"{phone}:{pin}:mdumeni-salt".encode()
    return hashlib.sha256(key).hexdigest()

def verify_pin(pin: str, phone: str, stored_hash: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    expected = hash_pin(pin, phone)
    return hmac.compare_digest(expected, stored_hash)

def create_token(farmer_id: str, phone: str) -> str:
    """Create a simple signed JWT token — 90 day expiry."""
    header  = base64.urlsafe_b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()

    payload = base64.urlsafe_b64encode(json.dumps({
        "farmer_id": farmer_id,
        "phone":     phone,
        "iat":       int(time.time()),
        "exp":       int(time.time()) + (90 * 24 * 3600),  # 90 days
    }).encode()).rstrip(b"=").decode()

    signature = base64.urlsafe_b64encode(
        hmac.new(
            JWT_SECRET.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256
        ).digest()
    ).rstrip(b"=").decode()

    return f"{header}.{payload}.{signature}"

def verify_token(token: str) -> dict | None:
    """Verify token signature and expiry. Returns payload or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(
                JWT_SECRET.encode(),
                f"{header}.{payload}".encode(),
                hashlib.sha256
            ).digest()
        ).rstrip(b"=").decode()

        if not hmac.compare_digest(expected_sig, signature):
            return None

        # Decode payload
        padded = payload + "=" * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))

        if data.get("exp", 0) < time.time():
            return None  # Expired

        return data
    except Exception:
        return None

def normalize_phone(phone: str) -> str:
    """Normalize Zimbabwe phone numbers to +263XXXXXXXXX format."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("07") or phone.startswith("08"):
        phone = "+263" + phone[1:]
    elif phone.startswith("263"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+263" + phone
    return phone
