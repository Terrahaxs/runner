from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    token_header: str = 'X-Token'
    api_url: str = Field("https://api.terrahaxs.com", const=True)
    version: str = Field("0.0.14", const=True)
    allowed_orgs: str = Field(default="*", env="ALLOWED_ORGS")
    allowed_repos: str = Field(default="*", env="ALLOWED_REPOS")
    allowed_projects: str = Field(default="*", env="ALLOWED_PROJECTS")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


settings = Settings()
