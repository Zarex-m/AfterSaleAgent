from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AfterSaleAgent"
    api_prefix: str = "/api"


settings = Settings()