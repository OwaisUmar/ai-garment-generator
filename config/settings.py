from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    REDIS_URL: str = 'redis://redis:6379/0'
    DATABASE_URL: str
    OPENAI_API_KEY: str
    API_URL: str = 'http://localhost:8000'
    
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
    )
    
settings = Settings()