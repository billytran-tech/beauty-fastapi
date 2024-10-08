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

    SENTRY_DSN: str

    AWS_BUCKET_REGION: str
    AWS_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    PAYMENT_RETURN_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
