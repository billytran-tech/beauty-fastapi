# FastAPI Application
This is a simple FastAPI application for the Suav Beauty API.

## Requirements
see `requirements.txt`

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. From the root directory, start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
    This will start the server on `http://127.0.0.1:8000`. The `--reload` option will enable hot reloading, allowing you to see code changes without restarting the server.
