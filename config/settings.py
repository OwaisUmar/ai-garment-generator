from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    REDIS_URL: str
    DATABASE_URL: str
    OPENAI_API_KEY: str
    API_URL: str
    PUBLIC_API_URL: str
    
    
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
    )
    
settings = Settings()