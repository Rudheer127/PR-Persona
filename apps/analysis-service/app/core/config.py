from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Hugging Face LLM Config
    hf_token: str
    hf_base_url: str = "https://router.huggingface.co/v1"
    hf_model_name: str = "HuggingFaceH4/zephyr-7b-beta:featherless-ai"
    
    # Supabase Config
    supabase_url: str
    supabase_service_role_key: str
    
    # Internal Auth
    analysis_service_api_key: str
    
    # Rate Limits
    rate_limit_per_user_daily: int = 50
    rate_limit_per_org_daily: int = 200

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
