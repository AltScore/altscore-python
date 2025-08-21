from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class ActionableAPIDTO(BaseModel):
    id: str = Field(alias="id")
    workflow_id: str = Field(alias="workflowId")
    from_execution_id: str = Field(alias="fromExecutionId")
    
    assigned_to: Optional[str] = Field(alias="assignedTo", default=None)
    status: str = Field(alias="status")
    priority: int = Field(alias="priority")
    
    title: Optional[str] = Field(alias="title", default=None)
    message: Optional[str] = Field(alias="message", default=None)
    
    context: Dict[str, Any] = Field(alias="context")
    
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateActionableRequest(BaseModel):
    workflow_id: str = Field(alias="workflowId")
    from_execution_id: str = Field(alias="fromExecutionId")
    
    assigned_to: Optional[str] = Field(alias="assignedTo", default=None)
    status: Optional[str] = Field(alias="status", default="pending")
    priority: Optional[int] = Field(alias="priority", default=0)
    
    title: Optional[str] = Field(alias="title", default=None)
    message: Optional[str] = Field(alias="message", default=None)
    
    context: Optional[Dict[str, Any]] = Field(alias="context", default={})

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateActionableRequest(BaseModel):
    assigned_to: Optional[str] = Field(alias="assignedTo", default=None)
    status: Optional[str] = Field(alias="status", default=None)
    priority: Optional[int] = Field(alias="priority", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    message: Optional[str] = Field(alias="message", default=None)
    context: Optional[Dict[str, Any]] = Field(alias="context", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ActionableSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "actionables", header_builder, renew_token, ActionableAPIDTO.parse_obj(data))


class ActionableAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "actionables", header_builder, renew_token, ActionableAPIDTO.parse_obj(data))


class ActionablesSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=ActionableSync, retrieve_data_model=ActionableAPIDTO,
                         create_data_model=CreateActionableRequest, update_data_model=UpdateActionableRequest, resource="actionables")


class ActionablesAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=ActionableAsync, retrieve_data_model=ActionableAPIDTO,
                         create_data_model=CreateActionableRequest, update_data_model=UpdateActionableRequest, resource="actionables")