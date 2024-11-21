from pydantic import BaseModel, Field
from typing import Optional, Dict, List

from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
import httpx
import datetime as dt


EXECUTION_BATCH_STATUS_PENDING = "pending"
EXECUTION_BATCH_STATUS_PRE_PROCESSING = "pre_processing"
EXECUTION_BATCH_STATUS_PRE_PROCESSING_COMPLETE = "pre_processing_complete"
EXECUTION_BATCH_STATUS_PROCESSING = "processing"
EXECUTION_BATCH_STATUS_PROCESSING_COMPLETE = "processing_complete"
EXECUTION_BATCH_STATUS_POST_PROCESSING = "post_processing"
EXECUTION_BATCH_STATUS_COMPLETE = "complete"
EXECUTION_BATCH_STATUS_PAUSED = "paused"
EXECUTION_BATCH_STATUS_CANCELLED = "cancelled"
EXECUTION_BATCH_STATUS_FAILED = "failed"


class CreateExecutionBatchDTO(BaseModel):
    status: str = Field(alias="status")
    workflow_id: Optional[str] = Field(alias="workflowId", default=None)
    workflow_alias: Optional[str] = Field(alias="workflowAlias", default=None)
    workflow_version: Optional[str] = Field(alias="workflowVersion", default=None)
    callback_at: dt.datetime = Field(alias="callbackAt")
    principal_id: Optional[str] = Field(alias="principalId", default=None)
    is_billable: Optional[bool] = Field(alias="isBillable", default=None)
    state: Optional[Dict] = Field(alias="state", default={})
    tags: Optional[List[str]] = Field(alias="tags", default=[])
    label: Optional[str] = Field(alias="label", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    inputs: Optional[Dict] = Field(alias="inputs", default=None)
    debug: Optional[bool] = Field(alias="debug", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateExecutionBatchDTO(BaseModel):
    status: Optional[str] = Field(alias="status", default=None)
    callback_at: Optional[dt.datetime] = Field(alias="callbackAt", default=None)
    state: Optional[Dict] = Field(alias="state", default=None)
    inputs: Optional[Dict] = Field(alias="inputs", default=None)
    outputs: Optional[Dict] = Field(alias="outputs", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ExecutionBatchAPIDTO(BaseModel):
    id: str = Field(alias="id")
    status: str = Field(alias="status")
    callback_at: str = Field(alias="callbackAt")
    state: Dict = Field(alias="state")
    label: Optional[str] = Field(alias="label", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    workflow_id: Optional[str] = Field(alias="workflowId", default=None)
    workflow_alias: Optional[str] = Field(alias="workflowAlias", default=None)
    workflow_version: Optional[str] = Field(alias="workflowVersion", default=None)
    is_billable: Optional[bool] = Field(alias="isBillable", default=None)
    tenant: str = Field(alias="tenant")
    tags: List[str] = Field(alias="tags")
    principal_id: Optional[str] = Field(alias="principalId", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    finished_at: Optional[str] = Field(alias="finishedAt", default=None)
    is_success: Optional[bool] = Field(alias="isSuccess", default=None)
    inputs: Optional[Dict] = Field(alias="inputs", default=None)
    outputs: Optional[Dict] = Field(alias="outputs", default=None)
    debug: Optional[bool] = Field(alias="debug", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ExecutionBatch(BaseModel):
    execution_batch_id: str
    status: str
    callback_at: dt.datetime
    state: Dict
    label: Optional[str]
    description: Optional[str]
    workflow_id: Optional[str]
    workflow_alias: Optional[str]
    workflow_version: Optional[str]
    is_billable: Optional[bool]
    tags: List[str]
    principal_id: Optional[str]
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
    finished_at: Optional[dt.datetime]
    is_success: Optional[bool]
    inputs: Optional[Dict]
    outputs: Optional[Dict]
    debug: Optional[bool]

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ExecutionBatchAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "execution-batches", header_builder, renew_token, ExecutionBatchAPIDTO.parse_obj(data))

    def _execution_batch(self, resource_id):
        return f"{self.base_url}/v1/{self.resource}/{resource_id}"


    @retry_on_401_async
    async def patch(self,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        status: Optional[str] = None,
        callback_at: Optional[dt.datetime] = None,
        state: Optional[Dict] = None
    ):
        payload = {
            "inputs": inputs,
            "outputs": outputs,
            "status": status,
            "callbackAt": callback_at,
            "state": state
        }

        with httpx.AsyncClient() as client:
            response = await client.patch(
                self._execution_batch(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300
            )

            raise_for_status_improved(response)
            self.data = ExecutionBatchAPIDTO.parse_obj(response.json())


class ExecutionBatchAsyncModule(GenericAsyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=ExecutionBatchAsync, retrieve_data_model=ExecutionBatchAPIDTO,
                         create_data_model=CreateExecutionBatchDTO, update_data_model=UpdateExecutionBatchDTO, resource="execution-batches")


class ExecutionBatchSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "execution-batches", header_builder, renew_token, ExecutionBatchAPIDTO.parse_obj(data))

    def _execution_batch(self, resource_id):
        return f"{self.base_url}/v1/{self.resource}/{resource_id}"

    @retry_on_401
    def patch(self,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        status: Optional[str] = None,
        callback_at: Optional[dt.datetime] = None,
        state: Optional[Dict] = None
    ):
        payload = {
            "inputs": inputs,
            "outputs": outputs,
            "status": status,
            "callbackAt": callback_at,
            "state": state
        }

        with httpx.Client() as client:
            response = client.patch(
                self._execution_batch(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300
            )

            raise_for_status_improved(response)
            self.data = ExecutionBatchAPIDTO.parse_obj(response.json())


class ExecutionBatchSyncModule(GenericSyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=ExecutionBatchSync, retrieve_data_model=ExecutionBatchAPIDTO,
                         create_data_model=CreateExecutionBatchDTO, update_data_model=UpdateExecutionBatchDTO, resource="execution-batches")
