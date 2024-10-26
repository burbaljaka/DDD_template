from pydantic_settings import BaseSettings as _BaseSettings


class BaseSettings(_BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
