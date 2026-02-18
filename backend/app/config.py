from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    turso_database_url: str = ""
    turso_auth_token: str = ""
    chroma_persist_dir: str = "./chroma_db"
    allowed_origins: str = "http://localhost:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = {"env_file": ".env"}


settings = Settings()
