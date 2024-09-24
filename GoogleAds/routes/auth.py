from fastapi import APIRouter, HTTPException, Request, Response
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from models.schemas import AuthRequest
from typing import Dict, Any
import uuid

from services.google_ads_manager import GoogleAdsManager

router = APIRouter()

state_store: Dict[str, Dict[str, Any]] = {}
global_credentials = None
global_customer_id = None

def generate_state():
    return str(uuid.uuid4())

def authentication_google(customer_id: str, credentials: dict):
    global global_credentials, global_customer_id
    
    if 'web' not in credentials:
        raise ValueError(f"Credentials must contain a 'web' key. Received keys: {list(credentials.keys())}")
    
    client_config = credentials['web']
    refresh_token = client_config.get("refresh_token")
    
    if refresh_token:
        global_credentials = Credentials.from_authorized_user_info(
            {
                "client_id": client_config["client_id"],
                "client_secret": client_config["client_secret"],
                "refresh_token": refresh_token
            },
            scopes=['https://www.googleapis.com/auth/adwords']
        )
        global_customer_id = customer_id
        return global_credentials
    
    flow = Flow.from_client_config(
        client_config={'web': client_config},
        scopes=['https://www.googleapis.com/auth/adwords'],
    )
    
    flow.redirect_uri = "http://127.0.0.1:8000/oauth2callback"

    global_credentials = credentials
    global_customer_id = customer_id

    state = generate_state()
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        state=state
    ) 
    state_store[state] = {
        "customer_id": customer_id,
        "credentials": credentials
    }
    return {"state": state, "auth_url": auth_url}

@router.post("/authenticate")
async def authenticate(auth_request: AuthRequest):
    try:
        auth_result = authentication_google(auth_request.customer_id, auth_request.credentials)
        if isinstance(auth_result, dict):
            return Response(content=json.dumps(auth_result), media_type="application/json")
        elif hasattr(auth_result, 'to_json'):
            return Response(content=auth_result.to_json(), media_type="application/json")
        else:
            return Response(content=json.dumps({
                "token": auth_result.token,
                "refresh_token": auth_result.refresh_token,
                "token_uri": auth_result.token_uri,
                "client_id": auth_result.client_id,
                "client_secret": auth_result.client_secret,
                "scopes": auth_result.scopes
            }), media_type="application/json")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/oauth2callback")
async def oauth2callback(request: Request):
    try:
        state = request.query_params.get("state")
        if not state or state not in state_store:
            raise HTTPException(status_code=400, detail="Invalid or expired state")

        stored_state = state_store[state]
        flow = Flow.from_client_config(
            client_config={'web': stored_state['credentials']['web']},
            scopes=['https://www.googleapis.com/auth/adwords']
        )
        flow.redirect_uri = request.url_for("oauth2callback")

        authorization_response = str(request.url)
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        refresh_token = credentials.refresh_token
        state_store[state]["refresh_token"] = refresh_token

        html_content = """
        <html>
            <head>
                <title>Authentication Complete</title>
                <script type="text/javascript">
                    window.close();
                </script>
            </head>
            <body>
                <h1>Authentication complete. You can now close this window.</h1>
            </body>
        </html>
        """
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to complete authentication: {str(e)}")

@router.get("/check_auth_status/{state}")
async def check_auth_status(state: str):
    if state not in state_store:
        raise HTTPException(status_code=404, detail="State not found")
    
    refresh_token = state_store[state].get("refresh_token")
    if refresh_token:
        return {"status": "complete", "refresh_token": refresh_token}
    else:
        return {"status": "pending"}

@router.post("/complete_auth_and_get_campaigns")
async def complete_auth_and_get_campaigns(request: Request):
    data = await request.json()
    customer_id = data.get("customer_id")
    refresh_token = data.get("refresh_token")
    credentials = data.get("credentials")

    try:
        credentials['web']['refresh_token'] = refresh_token
        manager = GoogleAdsManager(client=credentials, customer_id=customer_id)
        campaigns = manager.get_ad_campaigns()
        return {"campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete operation: {str(e)}")
