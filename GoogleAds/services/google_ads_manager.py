import datetime
import logging
import time
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)

class GoogleAdsManager:
    def __init__(self, client, customer_id):
        self.customer_id = str(customer_id).replace('-', '') 
        if not self.customer_id.isdigit() or len(self.customer_id) != 10:
            raise ValueError(f"Invalid customer ID format: {self.customer_id}. It must be a 10-digit number.")
        
        self.credentials = client  
        self.developer_token = client['developer_token']

    def initialize_client(self):
        self.client = GoogleAdsClient.load_from_dict({
            "use_proto_plus": True,
            "developer_token": self.developer_token,
            "client_id": self.credentials['client_id'],
            "client_secret": self.credentials['client_secret'],
            "refresh_token": self.credentials['refresh_token'],
            "login_customer_id": self.customer_id,
            "scopes": self.credentials['scopes']
        })

    def get_ad_campaigns(self):
        try:
            self.initialize_client()
            child_accounts = self.get_customer_ids()
            campaigns_dict = {}

            for account in child_accounts:
                ga_service = self.client.get_service("GoogleAdsService")
                query = """
                    SELECT
                    campaign.id,
                    campaign.name,
                    campaign_budget.amount_micros
                    FROM campaign
                    WHERE campaign.status != 'REMOVED'
                    ORDER BY campaign.id
                """
                response = ga_service.search(customer_id=account['id'], query=query)
                campaign_details = []
                for row in response:
                    campaign = row.campaign
                    campaign_details.append({
                        "Campaign ID": campaign.id,
                        "Campaign Name": campaign.name,
                        "Budget": row.campaign_budget.amount_micros / 1000000
                    })
                campaigns_dict[account['id']] = {
                    "Account Name": account['name'],
                    "Campaigns": campaign_details
                }
            return campaigns_dict
        except GoogleAdsException as ex:
            logger.error(f'A Google Ads API error occurred: {ex}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise

    def create_campaign(self, campaign_name, daily_budget, start_date, end_date):
        try:
            self.initialize_client()
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            campaign_service = self.client.get_service("CampaignService")

            # Create campaign budget
            campaign_budget_operation = self.client.get_type("CampaignBudgetOperation")
            campaign_budget = campaign_budget_operation.create
            campaign_budget.name = f"Budget for {campaign_name}"
            campaign_budget.amount_micros = int(daily_budget * 1000000)
            campaign_budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD

            # Mutate budget
            response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[campaign_budget_operation]
            )
            budget_resource_name = response.results[0].resource_name

            # Create campaign
            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = campaign_name
            campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = self.client.enums.CampaignStatusEnum.PAUSED
            campaign.manual_cpc.enhanced_cpc_enabled = True
            campaign.campaign_budget = budget_resource_name
            campaign.start_date = datetime.date.strftime(start_date, "%Y%m%d")
            campaign.end_date = datetime.date.strftime(end_date, "%Y%m%d")

            # Mutate campaign
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )

            return response.results[0].resource_name

        except GoogleAdsException as ex:
            logger.error(f'A Google Ads API error occurred: {ex}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise

    def update_campaign_budget(self, campaign_name, new_budget):
        try:
            self.initialize_client()
            ga_service = self.client.get_service("GoogleAdsService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")

            # Find the campaign by name
            query = f"""
                SELECT 
                    campaign.id,
                    campaign_budget.resource_name,
                    campaign_budget.amount_micros
                FROM campaign
                WHERE campaign.name = '{campaign_name}'
                AND campaign.status != 'REMOVED'
            """
            response = ga_service.search(customer_id=self.customer_id, query=query)

            campaign_budget_resource_name = None
            for row in response:
                campaign_budget_resource_name = row.campaign_budget.resource_name
                break

            if campaign_budget_resource_name is None:
                logger.error(f"No campaign found with name: {campaign_name}")
                return False

            # Update the budget
            campaign_budget_operation = self.client.get_type("CampaignBudgetOperation")
            campaign_budget = campaign_budget_operation.update
            campaign_budget.resource_name = campaign_budget_resource_name
            campaign_budget.amount_micros = int(new_budget * 1000000)

            field_mask = self.client.get_type("FieldMask")
            field_mask.paths.append("amount_micros")
            campaign_budget_operation.update_mask.CopyFrom(field_mask)

            campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[campaign_budget_operation]
            )

            logger.info(f"Successfully updated budget for campaign: {campaign_name}")
            return True

        except GoogleAdsException as ex:
            logger.error(f'A Google Ads API error occurred: {ex}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise

    def get_customer_ids(self):
        ga_service = self.client.get_service("GoogleAdsService")
        query = """
            SELECT
            customer_client.id,
            customer_client.descriptive_name
            FROM customer_client
            WHERE customer_client.manager = FALSE
        """
        stream = ga_service.search_stream(customer_id=self.customer_id, query=query)
            
        client_customers = []
        for batch in stream:
            for row in batch.results:
                client_customers.append({
                    'id': str(row.customer_client.id),
                    'name': row.customer_client.descriptive_name
                })
        return client_customers

    def get_campaign_id_by_name(self, campaign_name):
        if not self.client:
            raise ValueError("Google Ads Client is not initialized")
        
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT campaign.id
                FROM campaign
                WHERE campaign.name = '{campaign_name}'
                AND campaign.status != 'REMOVED'
                LIMIT 1
            """
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            for row in response:
                return row.campaign.id
            
            return None  
        except GoogleAdsException as ex:
            logger.error(f'A Google Ads API error occurred: {ex}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise
                
    def create_search_ad(self, campaign_name, headlines, descriptions, keywords, business_website):
        self.initialize_client()
        try:
            # Get the campaign
            campaign_id = self.get_campaign_id_by_name(campaign_name)
            
            if not campaign_id:
                raise ValueError(f"Campaign '{campaign_name}' not found")

            # Create a unique ad group name
            ad_group_name = f"Ad Group for {campaign_name} - {int(time.time())}"

            # Create ad group
            ad_group_service = self.client.get_service("AdGroupService")
            ad_group_operation = self.client.get_type("AdGroupOperation")
            ad_group = ad_group_operation.create
            ad_group.name = ad_group_name
            ad_group.campaign = self.client.get_service("CampaignService").campaign_path(self.customer_id, campaign_id)
            ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD

            # Add the ad group
            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=self.customer_id, operations=[ad_group_operation]
            )
            ad_group_resource_name = ad_group_response.results[0].resource_name

            # Create responsive search ad
            ad_group_ad_operation = self.client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_group_ad_operation.create
            ad_group_ad.ad_group = ad_group_resource_name
            ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED

            # Create the ad
            ad = ad_group_ad.ad
            for headline in headlines:
                ad.responsive_search_ad.headlines.append({"text": headline})
            for description in descriptions:
                ad.responsive_search_ad.descriptions.append({"text": description})
            ad.final_urls.append(business_website)

            # Add the ad
            ad_service = self.client.get_service("AdGroupAdService")
            ad_response = ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id, operations=[ad_group_ad_operation]
            )

            # Add keywords
            ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
            criterion_operations = []
            for keyword in keywords:
                criterion_operation = self.client.get_type("AdGroupCriterionOperation")
                criterion = criterion_operation.create
                criterion.ad_group = ad_group_resource_name
                criterion.keyword.text = keyword
                criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum.EXACT
                criterion_operations.append(criterion_operation)

            keyword_response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id, operations=criterion_operations
            )

            return ad_group_resource_name

        except GoogleAdsException as ex:
            error_message = f"Google Ads API error occurred: {ex}"
            for error in ex.failure.errors:
                error_message += f"\n\tError with message '{error.message}'."
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        error_message += f"\n\t\tOn field: {field_path_element.field_name}"
            raise Exception(error_message)
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            raise
    
    def upload_logo(self, campaign_name, file):
        self.initialize_client()
        asset_service = self.client.get_service("AssetService")
        asset_operation = self.client.get_type("AssetOperation")
        asset = asset_operation.create
        asset.name = f"{campaign_name} Logo"
        asset.image_asset.data = file.file.read()
        asset.image_asset.mime_type = self.client.enums.MimeTypeEnum.IMAGE_PNG
        response = asset_service.mutate_assets(customer_id=self.customer_id, operations=[asset_operation])
        return response.results[0].resource_name

    def upload_price(self, campaign_name, price):
        self.initialize_client()
        asset_service = self.client.get_service("AssetService")
        asset_operation = self.client.get_type("AssetOperation")
        asset = asset_operation.create
        asset.name = f"{campaign_name} Price"
        asset.price_asset.price = price
        response = asset_service.mutate_assets(customer_id=self.customer_id, operations=[asset_operation])
        return response.results[0].resource_name

    def get_logo_assets(self):
        self.initialize_client()
        ga_service = self.client.get_service("GoogleAdsService")
        query = """
            SELECT
                asset.resource_name,
                asset.name,
                asset.image_asset.file_size,
                asset.image_asset.full_size.width_pixels,
                asset.image_asset.full_size.height_pixels,
                asset.image_asset.full_size.url
            FROM asset
            WHERE asset.type = IMAGE
            AND asset.name LIKE '%Logo%'
        """
        response = ga_service.search(customer_id=self.customer_id, query=query)
        logo_assets = []
        for row in response:
            asset = row.asset
            logo_assets.append({
                "resource_name": asset.resource_name,
                "name": asset.name,
                "file_size": asset.image_asset.file_size,
                "width": asset.image_asset.full_size.width_pixels,
                "height": asset.image_asset.full_size.height_pixels,
                "url": asset.image_asset.full_size.url
            })
        return logo_assets

    def get_price_assets(self):
        self.initialize_client()
        ga_service = self.client.get_service("GoogleAdsService")
        query = """
            SELECT
                asset.resource_name,
                asset.name,
                asset.price_asset.type,
                asset.price_asset.price_offering.header,
                asset.price_asset.price_offering.description,
                asset.price_asset.price_offering.price.amount_micros,
                asset.price_asset.price_offering.price.currency_code,
                asset.price_asset.price_offering.unit
            FROM asset
            WHERE asset.type = PRICE
        """
        response = ga_service.search(customer_id=self.customer_id, query=query)
        price_assets = []
        for row in response:
            asset = row.asset
            price_assets.append({
                "resource_name": asset.resource_name,
                "name": asset.name,
                "type": asset.price_asset.type,
                "header": asset.price_asset.price_offering.header,
                "description": asset.price_asset.price_offering.description,
                "price_amount": asset.price_asset.price_offering.price.amount_micros / 1000000,
                "currency_code": asset.price_asset.price_offering.price.currency_code,
                "unit": asset.price_asset.price_offering.unit
            })
        return price_assets