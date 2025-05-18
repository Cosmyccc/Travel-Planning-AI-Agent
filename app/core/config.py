from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # # Database settings
    # DATABASE_URL: str = "postgresql://user:password@localhost:5432/travel_planner"
    
    # Security settings
    SECRET_KEY: str = "0fb5ddfe8c0c550a8639896112640bdbf810cd93a8a4e0b2fde8b2f7459dfc4d"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys (to be added later)
    WEATHER_API_KEY: str = ""
    FLIGHT_API_KEY: str = ""
    HOTEL_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 