# FastAPI MongoDB Update Service

This is a simple FastAPI application that provides an endpoint to update items in a MongoDB collection.

## Requirements

- Python 3.7+
- FastAPI
- Pydantic
- PyMongo
- MongoDB

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/fastapi-mongodb-update-service.git
    cd fastapi-mongodb-update-service
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set the MongoDB connection string in your environment variables:
    ```sh
    export MONGO="your_mongodb_connection_string"
    ```

## Running the Application

Start the FastAPI server: