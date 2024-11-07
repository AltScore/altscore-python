from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List

from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
import httpx
import datetime as dt


BATCH_EXECUTION_STATUS_PENDING = "pending"
BATCH_EXECUTION_STATUS_SCHEDULED = "scheduled"
BATCH_EXECUTION_STATUS_PRE_PROCESSING = "pre_processing"
BATCH_EXECUTION_STATUS_PRE_PROCESSING_COMPLETE = "pre_processing_complete"
BATCH_EXECUTION_STATUS_PROCESSING = "processing"
BATCH_EXECUTION_STATUS_PROCESSING_COMPLETE = "processing_complete"
BATCH_EXECUTION_STATUS_POST_PROCESSING = "post_processing"
BATCH_EXECUTION_STATUS_COMPLETE = "complete"
BATCH_EXECUTION_STATUS_PAUSED = "paused"
BATCH_EXECUTION_STATUS_CANCELLED = "cancelled"


class UpdateBatchExecutionDTO(BaseModel):
    status: Optional[str] = Field(alias="status", default=None)
    callback_at: Optional[dt.datetime] = Field(alias="callbackAt", default=None)
    state: Optional[Dict] = Field(alias="state", default=None)
    inputs: Optional[Dict] = Field(alias="inputs", default=None)
    outputs: Optional[Dict] = Field(alias="outputs", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class BatchExecutionAPIDTO(BaseModel):
    id: str = Field(alias="id")
    batch_id: str = Field(alias="batchId")
    status: str = Field(alias="status")
    callback_at: str = Field(alias="callbackAt")
    state: Dict = Field(alias="state")
    workflow_id: Optional[str] = Field(alias="workflowId", default=None)
    workflow_alias: Optional[str] = Field(alias="workflowAlias", default=None)
    workflow_version: Optional[str] = Field(alias="workflowVersion", default=None)
    tenant: str = Field(alias="tenant")
    tags: List[str] = Field(alias="tags")
    principal_id: Optional[str] = Field(alias="principalId", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    finished_at: Optional[str] = Field(alias="finishedAt", default=None)
    is_success: Optional[bool] = Field(alias="isSuccess", default=None)
    inputs: Optional[Dict] = Field(alias="inputs", default=None)
    outputs: Optional[Dict] = Field(alias="outputs", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class BatchExecution(BaseModel):
    batch_id: str
    batch_execution_id: str
    status: str
    callback_at: dt.datetime
    state: Dict
    workflow_id: Optional[str]
    workflow_alias: Optional[str]
    workflow_version: Optional[str]
    tags: List[str]
    principal_id: Optional[str]
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
    finished_at: Optional[dt.datetime]
    is_success: Optional[bool]
    inputs: Optional[Dict]
    outputs: Optional[Dict]

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    @validator("status")
    def status_must_be_valid(cls, v):
        valid_status = [
            BATCH_EXECUTION_STATUS_PENDING,
            BATCH_EXECUTION_STATUS_SCHEDULED,
            BATCH_EXECUTION_STATUS_PRE_PROCESSING,
            BATCH_EXECUTION_STATUS_PRE_PROCESSING_COMPLETE,
            BATCH_EXECUTION_STATUS_PROCESSING,
            BATCH_EXECUTION_STATUS_PROCESSING_COMPLETE,
            BATCH_EXECUTION_STATUS_POST_PROCESSING,
            BATCH_EXECUTION_STATUS_COMPLETE,
            BATCH_EXECUTION_STATUS_PAUSED,
            BATCH_EXECUTION_STATUS_CANCELLED
        ]

        if v not in valid_status:
            raise ValueError(f"Invalid status, must be one of {valid_status}")

        return v


class BatchExecutionAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "batch_executions", header_builder, renew_token, BatchExecutionAPIDTO.parse_obj(data))

    def _batch_execution(self, resource_id):
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
                self._batch_execution(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300
            )

            raise_for_status_improved(response)
            self.data = BatchExecutionAPIDTO.parse_obj(response.json())


class BatchExecutionAsyncModule(GenericAsyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=BatchExecutionAsync, retrieve_data_model=BatchExecutionAPIDTO,
                         create_data_model=None, update_data_model=UpdateBatchExecutionDTO, resource="batch_executions")


class BatchExecutionSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "batch_executions", header_builder, renew_token, BatchExecutionAPIDTO.parse_obj(data))

    def _batch_execution(self, resource_id):
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
                self._batch_execution(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300
            )

            raise_for_status_improved(response)
            self.data = BatchExecutionAPIDTO.parse_obj(response.json())


class BatchExecutionSyncModule(GenericSyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=BatchExecutionSync, retrieve_data_model=BatchExecutionAPIDTO,
                         create_data_model=None, update_data_model=UpdateBatchExecutionDTO, resource="batch_executions")
