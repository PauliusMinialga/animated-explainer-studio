from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mistral_api_key: str = ""

    # Supabase (optional — Paul's frontend uses this)
    supabase_url: str = ""
    supabase_key: str = ""


settings = Settings()
