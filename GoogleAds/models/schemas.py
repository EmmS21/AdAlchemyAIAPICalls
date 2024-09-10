from pydantic import BaseModel
from datetime import date
from typing import List

class CampaignCreate(BaseModel):
    customer_id: str
    campaign_name: str
    daily_budget: float
    start_date: date
    end_date: date
    credentials: dict

class BudgetUpdate(BaseModel):
    customer_id: str
    campaign_name: str
    new_budget: float
    credentials: dict

class CampaignsList(BaseModel):
    customer_id: str
    credentials: dict

class AuthRequest(BaseModel):
    customer_id: str
    credentials: dict

class AdCreate(BaseModel):
    customer_id: str
    campaign_name: str
    headlines: List[str]
    descriptions: List[str]
    keywords: List[str]
    credentials: dict