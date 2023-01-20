import os
from pydantic import BaseSettings, Field
from enum import Enum

class ModeEnum(str, Enum):
    api = 'api'
    sqs = 'sqs'
    github_action = 'github_action'

class Settings(BaseSettings):
    env: str = Field(..., env="ENV")
    mode: ModeEnum = Field(..., env='MODE')
    rollbar_key: str = Field(None, env='ROLLBAR_KEY')
    token_header: str = 'X-Token'

    api_url: str = Field(..., env='API_URL')
    version: str = Field(..., env='VERSION')
    self_hosted: bool = Field(True, env='SELF_HOSTED')

    class Config:
        env_file = '.test.env' if os.getenv('ENV') != 'prod' else '.env'
        env_file_encoding = 'utf-8'

settings = Settings()