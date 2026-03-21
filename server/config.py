from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    fal_key: str = ""
    avatar_image_url: str = (
        "https://v3.fal.media/files/koala/NLVPfOI4XL1cWT2PmmqT3_Hope.png"
    )
    supabase_url: str = ""
    supabase_key: str = ""

    # Supabase Storage bucket for generated videos
    video_bucket: str = "videos"


settings = Settings()
