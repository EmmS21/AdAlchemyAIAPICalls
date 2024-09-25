from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import AssetUpload
from services.google_ads_manager import GoogleAdsManager
from google.ads.googleads.errors import GoogleAdsException

router = APIRouter()

@router.post("/upload_logo")
async def upload_logo(asset: AssetUpload, file: UploadFile = File(...)):
    try:
        manager = GoogleAdsManager(client=asset.credentials, customer_id=asset.customer_id)
        result = manager.upload_logo(asset.campaign_name, file)
        return {"message": "Logo uploaded successfully", "asset_id": result}
    except GoogleAdsException as ex:
        error_message = f"Google Ads API error occurred: {ex}"
        for error in ex.failure.errors:
            error_message += f"\n\tError with message '{error.message}'."
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    error_message += f"\n\t\tOn field: {field_path_element.field_name}"
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_price")
async def upload_price(asset: AssetUpload, price: float):
    try:
        manager = GoogleAdsManager(client=asset.credentials, customer_id=asset.customer_id)
        result = manager.upload_price(asset.campaign_name, price)
        return {"message": "Price uploaded successfully", "asset_id": result}
    except GoogleAdsException as ex:
        error_message = f"Google Ads API error occurred: {ex}"
        for error in ex.failure.errors:
            error_message += f"\n\tError with message '{error.message}'."
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    error_message += f"\n\t\tOn field: {field_path_element.field_name}"
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get_logo_assets")
async def get_logo_assets(asset: AssetUpload):
    print("Received credentials:", asset)

    try:
        manager = GoogleAdsManager(client=asset.credentials.dict(), customer_id=asset.customer_id)
        result = manager.get_logo_assets()
        return {"message": "Logo assets retrieved successfully", "assets": result}
    except GoogleAdsException as ex:
        error_message = f"Google Ads API error occurred: {ex}"
        for error in ex.failure.errors:
            error_message += f"\n\tError with message '{error.message}'."
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    error_message += f"\n\t\tOn field: {field_path_element.field_name}"
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get_price_assets")
async def get_price_assets(asset: AssetUpload):
    try:
        manager = GoogleAdsManager(client=asset.credentials, customer_id=asset.customer_id)
        result = manager.get_price_assets()
        return {"message": "Price assets retrieved successfully", "assets": result}
    except GoogleAdsException as ex:
        error_message = f"Google Ads API error occurred: {ex}"
        for error in ex.failure.errors:
            error_message += f"\n\tError with message '{error.message}'."
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    error_message += f"\n\t\tOn field: {field_path_element.field_name}"
        raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))