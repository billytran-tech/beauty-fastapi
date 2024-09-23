from fastapi import FastAPI, status
from pydantic import BaseModel
from app.routers.v0 import customer, merchant, services, users, country, username, uploads, file_uploads
import sentry_sdk

from app.config.config import settings

_sentry_dsn = settings.SENTRY_DSN

sentry_sdk.init(
    dsn=_sentry_dsn,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title="Suav Beauty Technologies Inc. API for Web Application",
    description="The following documentation describes the API endpoints for the Suav Beauty Technologies Inc. These can be used by the frontend developers to build the web application with the required data.",
    version="1.0.0",
    openapi_url="/openapi.json",
)

app.include_router(users.router)
app.include_router(customer.router)
app.include_router(merchant.router)
app.include_router(services.router)
app.include_router(username.router)
app.include_router(country.router)
app.include_router(uploads.router)
app.include_router(uploads.router)


class WelcomeResponse(BaseModel):
    msg: str


@app.get("/", status_code=status.HTTP_200_OK, response_model=WelcomeResponse)
def read_root():
    """
    Handle the root endpoint of the API.

    This function handles GET requests to the root URL ("/") of the FastAPI application.
    When accessed, it returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message with the key "msg".

    """
    return {"msg": "Welcome to Suav Beauty"}
