from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Check server/.env first, then parent .env
        env_file=(".env", "../.env"),
        extra="ignore",
    )

    gemini_api_key: str = ""
    mistral_api_key: str = ""

    # Bote's pipeline
    fal_key: str = ""
    runware_api_key: str = ""

    # Default avatar image (fal.ai public URL — no upload needed)
    avatar_image_url: str = (
        "https://v3.fal.media/files/koala/NLVPfOI4XL1cWT2PmmqT3_Hope.png"
    )

    @property
    def llm_provider(self) -> str:
        """Gemini preferred; falls back to Mistral if no Gemini key."""
        return "gemini" if self.gemini_api_key else "mistral"


settings = Settings()
