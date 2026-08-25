from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./nimshop.db"
    frontend_url: str = "http://localhost:5173"
    nimiq_network: str = "testnet"
    nimiq_rpc_url: str = "https://node.nimiq.watch:443" # Configurable RPC endpoint
    ai_provider: str = "mock"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    search_query_max_length: int = 500

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()