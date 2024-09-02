from pydantic import EmailStr
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    DB_NAME: str

    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str

    AZURE_STORAGE_CONNECTION_STRING: str
    IMAGE_CONTAINER_NAME: str

    TWILIO_SID: str
    TWILIO_TOKEN: str
    TWILIO_VERIFICATION_SID: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
