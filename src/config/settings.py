import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SEARCH_GATEWAY_URL: str = Field(default="http://localhost:8002", validation_alias="SEARCH_GATEWAY_URL")
    
    # Legacy settings (can be removed if we are sure we don't need direct Weaviate access anymore)
    # WEAVIATE_HOST: str = Field(default="localhost", validation_alias="WEAVIATE_HOST")
    # WEAVIATE_PORT: int = Field(default=8080, validation_alias="WEAVIATE_PORT")
    # WEAVIATE_GRPC_PORT: int = Field(default=50051, validation_alias="WEAVIATE_GRPC_PORT")
    # TRANSFORMERS_URL: str = Field(default="http://localhost:9090/vectors", validation_alias="TRANSFORMERS_URL")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
