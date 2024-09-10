from fastapi import APIRouter, HTTPException
from models.schemas import CampaignCreate, BudgetUpdate, CampaignsList
from services.google_ads_manager import GoogleAdsManager

router = APIRouter()

@router.post("/get_campaigns")
def get_campaigns(campaigns_list: CampaignsList):
    try:
        # Remove hyphens from customer_id
        customer_id = str(campaigns_list.customer_id.replace('-', ''))
        if not customer_id.isdigit() or len(customer_id) != 10:
            raise ValueError("Invalid customer ID format. It must be a 10-digit number.")

        required_fields = ['refresh_token', 'token_uri', 'client_id', 'client_secret', 'developer_token']
        for field in required_fields:
            if field not in campaigns_list.credentials:
                raise ValueError(f"Missing required field: {field}")

        manager = GoogleAdsManager(client=campaigns_list.credentials, customer_id=campaigns_list.customer_id)
        manager.initialize_client()  
        campaigns = manager.get_ad_campaigns()
        return campaigns
    except ValueError as e:
        print(f"ValueError in get_campaigns: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in get_campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns: {str(e)}")

@router.post("/create_campaign")
def create_campaign(campaign: CampaignCreate):
    print('accessed')
    try:
        manager = GoogleAdsManager(client=campaign.credentials, customer_id=campaign.customer_id)
        result = manager.create_campaign(
            campaign.campaign_name,
            campaign.daily_budget,
            campaign.start_date,
            campaign.end_date
        )
        return {"message": "Campaign created successfully", "campaign_id": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update_campaign")
def update_campaign_budget(budget_update: BudgetUpdate):
    try:
        manager = GoogleAdsManager(client=budget_update.credentials, customer_id=budget_update.customer_id)
        result = manager.update_campaign_budget(budget_update.campaign_name, budget_update.new_budget)
        return {"message": "Campaign budget updated successfully", "success": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))