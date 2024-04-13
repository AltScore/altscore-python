from pydantic import BaseModel, Field
from typing import Optional, Dict
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class StepDataAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    principal_id: Optional[str] = Field(alias="principalId", default=None)
    order: int = Field(alias="order")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    created_at: str = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateStepDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class StepSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "steps", header_builder, renew_token, StepDataAPIDTO.parse_obj(data))


class StepAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "steps", header_builder, renew_token, StepDataAPIDTO.parse_obj(data))


class StepsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=StepSync,
                         retrieve_data_model=StepDataAPIDTO,
                         create_data_model=CreateStepDTO,
                         update_data_model=None,
                         resource="steps")


class StepsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=StepAsync,
                         retrieve_data_model=StepDataAPIDTO,
                         create_data_model=CreateStepDTO,
                         update_data_model=None,
                         resource="steps")
