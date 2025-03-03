from functools import lru_cache
from app.config import get_settings
from supabase import create_client, Client


settings = get_settings()

@lru_cache()
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)

@lru_cache()
def get_admin_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)
