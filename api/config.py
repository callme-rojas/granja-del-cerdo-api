from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql://granjacerdo_pdb_user:fkVQaTQeeg5KvgdkM0WKdaw9njrNCo8y@dpg-d4d3dammcj7s73cj6rs0-a.oregon-postgres.render.com/granjacerdo_pdb"
    
    # Autenticación
    JWT_SECRET: str = "mysecret123"
    
    # Servidor
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    RATE_LIMIT: str = "100/minute"
    
    # Machine Learning
    # Ajustado a la nueva estructura: los modelos viven en ml/models/
    MODEL_PATH: str = "ml/models/xgboost_24_features.pkl"
    DEFAULT_MARGIN_RATE: float = 0.10  # 10% de margen por defecto

    class Config:
         model_config = SettingsConfigDict(extra='ignore', env_file=".env")

settings = Settings()
