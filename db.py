# mdumeni-backend/db.py
# Supabase client — used by all endpoints
# Uses SERVICE ROLE key (bypasses RLS) — never expose this to the mobile app

import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://fhvsoqphnytsbzipqjsb.supabase.co"
)
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

_client: Client | None = None

def get_db() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "SUPABASE_SERVICE_KEY environment variable not set. "
                "Add it in Railway -> Variables."
            )
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client
