import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class WorkflowDataAPIDTO(BaseModel):
    id: str = Field(alias="id")
    execution_mode: str = Field(alias="executionMode")
    alias: str = Field(alias="alias")
    version: str = Field(alias="version")
    label: Optional[str] = Field(alias="label")
    description: Optional[str] = Field(alias="description")
    context: Optional[str] = Field(alias="context")
    flow_definition: Optional[dict] = Field(alias="flowDefinition")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class Lambda(BaseModel):
    url: str = Field(alias="url")
    headers: Dict[str, str] = Field(alias="headers", default={})


class CreateWorkflowDTO(BaseModel):
    label: Optional[str] = Field(alias="label")
    alias: str = Field(alias="alias")
    version: str = Field(alias="version")
    execution_mode: str = Field(alias="executionMode")
    description: Optional[str] = Field(alias="description")
    context: Optional[str] = Field(alias="context", default=None)
    flow_definition: Optional[dict] = Field(alias="flowDefinition")
    route: Optional[Lambda] = Field(alias="route", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateWorkflowDTO(BaseModel):
    label: Optional[str] = Field(alias="label")
    description: Optional[str] = Field(alias="description")
    route: Optional[Lambda] = Field(alias="route", default=None)
    flow_definition: Optional[dict] = Field(alias="flowDefinition")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class WorkflowExecutionResponseAPIDTO(BaseModel):
    execution_id: str = Field(alias="executionId")
    workflow_id: str = Field(alias="workflowId")
    workflow_alias: str = Field(alias="workflowAlias")
    workflow_version: str = Field(alias="workflowVersion")
    is_success: Optional[bool] = Field(alias="isSuccess")
    executed_at: str = Field(alias="executedAt")
    execution_output: Any = Field(alias="executionOutput")
    execution_custom_output: Any = Field(alias="executionCustomOutput")
    error_message: Optional[str] = Field(alias="errorMessage", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class WorkflowSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "workflows", header_builder, renew_token, WorkflowDataAPIDTO.parse_obj(data))


class WorkflowAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "workflows", header_builder, renew_token, WorkflowDataAPIDTO.parse_obj(data))


class WorkflowsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=WorkflowSync,
                         retrieve_data_model=WorkflowDataAPIDTO,
                         create_data_model=CreateWorkflowDTO,
                         update_data_model=UpdateWorkflowDTO,
                         resource="workflows")

    @retry_on_401
    def retrieve_by_alias_version(self, alias: str, version: str):
        query_params = {
            "alias": alias,
            "version": version
        }

        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                params=query_params,
                timeout=30
            )
            raise_for_status_improved(response)
            res = [self.sync_resource(
                base_url=self.altscore_client._borrower_central_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=self.retrieve_data_model.parse_obj(e)
            ) for e in response.json()]

            if len(res) == 0:
                return None
            return res[0]

    @retry_on_401
    def execute(self, workflow_input: Dict,
                workflow_id: Optional[str] = None,
                workflow_alias: Optional[str] = None,
                workflow_version: Optional[str] = None,
                ):
        if workflow_id is not None:
            with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
                response = client.post(
                    f"/v1/workflows/{workflow_id}/execute",
                    json=workflow_input,
                    headers=self.build_headers(),
                    timeout=900
                )
                raise_for_status_improved(response)
                return WorkflowExecutionResponseAPIDTO.parse_obj(response.json())

        elif workflow_alias is not None and workflow_version is not None:
            with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
                response = client.post(
                    f"/v1/workflows/{workflow_alias}/{workflow_version}/execute",
                    json=workflow_input,
                    headers=self.build_headers(),
                    timeout=900
                )
                raise_for_status_improved(response)
                return WorkflowExecutionResponseAPIDTO.parse_obj(response.json())
        else:
            raise ValueError("You must provide a workflow id or a workflow alias and version")


class WorkflowsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=WorkflowAsync,
                         retrieve_data_model=WorkflowDataAPIDTO,
                         create_data_model=CreateWorkflowDTO,
                         update_data_model=UpdateWorkflowDTO,
                         resource="workflows")

    @retry_on_401_async
    async def retrieve_by_alias_version(self, alias: str, version: str):
        query_params = {
            "alias": alias,
            "version": version
        }

        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                params=query_params,
                timeout=30
            )
            raise_for_status_improved(response)
            res = [self.async_resource(
                base_url=self.altscore_client._borrower_central_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=self.retrieve_data_model.parse_obj(e)
            ) for e in response.json()]

            if len(res) == 0:
                return None
            return res[0]

    @retry_on_401_async
    async def execute(self,
                      workflow_input: Dict,
                      workflow_id: Optional[str] = None,
                      workflow_alias: Optional[str] = None,
                      workflow_version: Optional[str] = None,
                      ):
        if workflow_id is not None:
            async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
                response = await client.post(
                    f"/v1/workflows/{workflow_id}/execute",
                    json=workflow_input,
                    headers=self.build_headers(),
                    timeout=900
                )
                raise_for_status_improved(response)
                return WorkflowExecutionResponseAPIDTO.parse_obj(response.json())

        elif workflow_alias is not None and workflow_version is not None:
            async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
                response = await client.post(
                    f"/v1/workflows/{workflow_alias}/{workflow_version}/execute",
                    json=workflow_input,
                    headers=self.build_headers(),
                    timeout=900
                )
                raise_for_status_improved(response)
                return WorkflowExecutionResponseAPIDTO.parse_obj(response.json())
        else:
            raise ValueError("You must provide a workflow id or a workflow alias and version")
