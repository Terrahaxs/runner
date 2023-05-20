from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    token_header: str = 'X-Token'
    api_url: str = Field("https://api.terrahaxs.com", const=True)
    version: str = Field("0.0.7", const=True)
    allowed_orgs: str = Field(default="*")
    allowed_repos: str = Field(default="*")
    allowed_projects: str = Field(default="*")

settings = Settings()