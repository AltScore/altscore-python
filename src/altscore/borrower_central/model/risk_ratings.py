from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class RiskRatingAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    value: str = Field(alias="value")
    history: List[Dict] = Field(alias="history")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateUpdateRiskRatingDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    value: str = Field(alias="value")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class RiskRatingSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "risk-ratings", header_builder, renew_token, RiskRatingAPIDTO.model_validate(data))


class RiskRatingAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "risk-ratings", header_builder, renew_token, RiskRatingAPIDTO.model_validate(data))


class RiskRatingsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=RiskRatingSync,
                         retrieve_data_model=RiskRatingAPIDTO,
                         create_data_model=CreateUpdateRiskRatingDTO,
                         update_data_model=CreateUpdateRiskRatingDTO,
                         resource="risk-ratings")


class RiskRatingsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=RiskRatingAsync,
                         retrieve_data_model=RiskRatingAPIDTO,
                         create_data_model=CreateUpdateRiskRatingDTO,
                         update_data_model=CreateUpdateRiskRatingDTO,
                         resource="risk-ratings")
