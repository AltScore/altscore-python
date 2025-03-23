from pydantic import BaseModel, Field
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from typing import Optional, Dict


class AutomationAPIDTO(BaseModel):
    id: str = Field(alias="id")
    trigger: str = Field(alias="trigger")
    workflow_id: str = Field(alias="workflowId")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateAutomationDTO(BaseModel):
    trigger: str = Field(alias="trigger")
    workflow_id: str = Field(alias="workflowId")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class AutomationsSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "automations", header_builder, renew_token, AutomationAPIDTO.model_validate(data))


class AutomationsAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "automations", header_builder, renew_token, AutomationAPIDTO.model_validate(data))


class AutomationsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=GenericSyncResource,
                         retrieve_data_model=AutomationAPIDTO,
                         create_data_model=CreateAutomationDTO,
                         update_data_model=CreateAutomationDTO,
                         resource="automations")


class AutomationsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=AutomationsAsync,
                         retrieve_data_model=AutomationAPIDTO,
                         create_data_model=CreateAutomationDTO,
                         update_data_model=CreateAutomationDTO,
                         resource="automations")
