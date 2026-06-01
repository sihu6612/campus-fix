import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    zhipu_api_key: str = os.getenv("ZHIPU_API_KEY", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    amap_api_key: str = os.getenv("AMAP_API_KEY", "")
    cors_origin: str = os.getenv("CORS_ORIGIN", "*")

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
