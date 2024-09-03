from fastapi import APIRouter, HTTPException
from models.schemas import AdCreate
from services.google_ads_manager import GoogleAdsManager
from google.ads.googleads.errors import GoogleAdsException

router = APIRouter()

@router.post("/create_ad")
def create_ad(ad: AdCreate):
    print('Received ad data:', ad.dict(exclude={'credentials'}))  
    try:
        manager = GoogleAdsManager(client=ad.credentials, customer_id=ad.customer_id)
        result = manager.create_search_ad(
            ad.campaign_name,
            ad.headlines,
            ad.descriptions,
            ad.keywords
        )
        return {"message": "Ad created successfully", "ad_group_id": result}
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