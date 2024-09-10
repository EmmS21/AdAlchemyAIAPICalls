# FastAPI Applications

This repository contains two FastAPI applications:

1. [Google Ads API FastAPI Application](#google-ads-api-fastapi-application)
2. [FastAPI MongoDB Update Service](#fastapi-mongodb-update-service)

## Google Ads API FastAPI Application

This FastAPI application provides an interface to interact with the Google Ads API. It offers endpoints for authentication, campaign management, and ad creation.

### Endpoints

#### Authentication

- **POST /authenticate**
  - Authenticates the user with Google Ads.
  - If a refresh token exists, it confirms authentication.
  - If no refresh token exists, it provides an auth URL for the OAuth flow.
  - Request body: `AuthRequest` (customer_id, credentials)
  - Response: Authentication status or auth URL

#### Campaigns

- **POST /get_campaigns**
  - Retrieves a list of campaigns for the authenticated user.
  - Request body: `CampaignsList` (customer_id, credentials)
  - Response: List of campaigns

- **POST /create_campaign**
  - Creates a new campaign.
  - Request body: `CampaignCreate` (customer_id, campaign_name, daily_budget, start_date, end_date, credentials)
  - Response: Confirmation message and campaign ID

- **POST /update_campaign**
  - Updates the budget of an existing campaign.
  - Request body: `BudgetUpdate` (customer_id, campaign_name, new_budget, credentials)
  - Response: Confirmation of update

#### Ads

- **POST /create_ad**
  - Creates a new search ad within a specified campaign.
  - Request body: `AdCreate` (customer_id, campaign_name, headlines, descriptions, keywords, credentials)
  - Response: Confirmation message and ad group ID

### Authentication Flow

1. Call `/authenticate` to start the authentication process.
2. If not authenticated, use the provided auth URL to complete the OAuth flow.
3. After OAuth completion, the application will store the refresh token for future use.

### Error Handling

All endpoints include error handling for various scenarios, including Google Ads API errors and general exceptions. Errors are returned with appropriate HTTP status codes and detailed error messages.

### Note

Ensure that you have the necessary Google Ads API credentials and permissions before using these endpoints. The application expects the credentials to be provided in the request body for each operation.

## FastAPI MongoDB Update Service

This is a simple FastAPI application that provides an endpoint to update items in a MongoDB collection.

### Requirements

- Python 3.7+
- FastAPI
- Pydantic
- PyMongo
- MongoDB

### Installation

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

### Running the Application

Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

### Endpoints

- **PUT /update_item**
  - Updates an item in the MongoDB collection.
  - Request body: `UpdateItemRequest` (item_id, update_data)
  - Response: Confirmation message

### Error Handling

The endpoint includes error handling for various scenarios, including MongoDB errors and general exceptions. Errors are returned with appropriate HTTP status codes and detailed error messages.

### Note

Ensure that you have the necessary MongoDB connection string set in your environment variables before running the application.