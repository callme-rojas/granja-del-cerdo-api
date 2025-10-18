from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://granjadelcerdo_pdb_user:Kuef1xTZUY9SxoggqmFxPDXo2LLkteWF@dpg-d3pa6q1r0fns73afp7h0-a.oregon-postgres.render.com/granjadelcerdo_pdb"
    JWT_SECRET: str = "mysecret123"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    RATE_LIMIT: str = "100/minute"

    class Config:
         model_config = SettingsConfigDict(extra='ignore', env_file=".env")

settings = Settings()
