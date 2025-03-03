import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')

@lru_cache()
def get_settings() -> Settings:
    return Settings()