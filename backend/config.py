import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nimshop.db")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    NIMIQ_RPC_URL: str = os.getenv("NIMIQ_RPC_URL", "https://rpc.testnet.nimiqwatch.com/")
    NIMIQ_NETWORK: str = os.getenv("NIMIQ_NETWORK", "testnet")
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")

    # Pydantic V2 configuration: load .env and ignore any extra unexpected variables
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
