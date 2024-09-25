from fastapi import FastAPI
from routes import auth, ads, campaigns, assets
import os

app = FastAPI()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app.include_router(auth.router, tags=["auth"])
app.include_router(campaigns.router, tags=["campaigns"])
app.include_router(ads.router, tags=["ads"])
app.include_router(assets.router, tags=["assets"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)