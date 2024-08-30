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

1. From the root directory, start the FastAPI server in development mode:
   This will start the development server on `http://127.0.0.1:8000`.
    ```bash
    fastapi dev
    ```

2. From the root directory, start the FastAPI server in production mode:
   This will start the production server on `http://0.0.0.0:8000`.

   ```bash
   fastapi run
   ```
