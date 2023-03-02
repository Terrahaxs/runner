from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    token_header: str = 'X-Token'
    api_url: str = Field("https://api.terrahaxs.com", const=True)
    version: str = Field("0.0.2", const=True)

settings = Settings()