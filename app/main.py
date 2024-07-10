from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI(
    title="Suav Beauty Technologies Inc. API for Web Application",
    description="The following documentation describes the API endpoints for the Suav Beauty Technologies Inc. These can be used by the frontend developers to build the web application with the required data.",
    version="1.0.0",
    openapi_url="/openapi.json",
)


class WelcomeResponse(BaseModel):
    # A Pydantic model for the response of the root endpoint
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
