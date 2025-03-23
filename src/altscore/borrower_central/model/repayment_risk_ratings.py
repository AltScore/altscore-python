from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class RepaymentRiskRatingAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    value: int = Field(alias="value")
    history: List[Dict] = Field(alias="history")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateRepaymentRiskRatingDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    value: int = Field(alias="value")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class RepaymentRiskRatingSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "repayment-risk-ratings", header_builder, renew_token,
                         RepaymentRiskRatingAPIDTO.model_validate(data))


class RepaymentRiskRatingAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "repayment-risk-ratings", header_builder, renew_token,
                         RepaymentRiskRatingAPIDTO.model_validate(data))


class RepaymentRiskRatingsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=RepaymentRiskRatingSync,
                         retrieve_data_model=RepaymentRiskRatingAPIDTO,
                         create_data_model=CreateRepaymentRiskRatingDTO,
                         update_data_model=CreateRepaymentRiskRatingDTO,
                         resource="repayment-risk-ratings")


class RepaymentRiskRatingsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=RepaymentRiskRatingAsync,
                         retrieve_data_model=RepaymentRiskRatingAPIDTO,
                         create_data_model=CreateRepaymentRiskRatingDTO,
                         update_data_model=CreateRepaymentRiskRatingDTO,
                         resource="repayment-risk-ratings")
