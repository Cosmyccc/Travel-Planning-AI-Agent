from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/travel_planner"
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    WEATHER_API_KEY: str = ""
    FLIGHT_API_KEY: str = ""
    HOTEL_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 