import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule

class ListStatus:
    PENDING = "pending"
    APPLIED = "applied"
    NO_HIT = "no_hit"

class SimilarEntity(BaseModel):
    entity_type: str = Field(alias="entityType")
    key: str = Field(alias="key")
    proposed_value: str = Field(alias="proposedValue")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class Similar(BaseModel):
    label: str = Field(alias="label")
    description: Optional[str] = Field(None, alias="description")
    entities: List[SimilarEntity] = Field(alias="entities")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ListOfSimilarAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    execution_id: Optional[str] = Field(None, alias="executionId")
    list_of_similar: List[Similar] = Field(alias="listOfSimilar")
    status: Optional[str] = Field(None, alias="status")
    applied_by: Optional[str] = Field(None, alias="appliedBy")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateListOfSimilar(BaseModel):
    borrower_id: Optional[str] = Field(None, alias="borrowerId")
    execution_id: Optional[str] = Field(None, alias="executionId")
    list_of_similar: List[Similar] = Field(alias="listOfSimilar")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ListOfSimilarSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "list-of-similar", header_builder, renew_token, ListOfSimilarAPIDTO.model_validate(data))

    @retry_on_401
    def apply(self, index: int, retry_workflow: bool = False):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v1/list-of-similar/{self.data.id}/apply",
                headers=self._header_builder(),
                timeout=300,
                json={
                    "index": index,
                    "retryWorkflow": retry_workflow
                }
            )
            raise_for_status_improved(response)

    @retry_on_401
    def report_no_hit(self, retry_workflow: bool = False):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v1/list-of-similar/{self.data.id}/no-hit",
                headers=self._header_builder(),
                timeout=300,
                json={
                    "retryWorkflow": retry_workflow
                }
            )
            raise_for_status_improved(response)


class ListOfSimilarAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "list-of-similar", header_builder, renew_token, ListOfSimilarAPIDTO.model_validate(data))

    @retry_on_401_async
    async def apply(self, index: int, retry_workflow: bool = False):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v1/list-of-similar/{self.data.id}/apply",
                headers=self._header_builder(),
                timeout=300,
                json={
                    "index": index,
                    "retryWorkflow": retry_workflow
                }
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def report_no_hit(self, retry_workflow: bool = False):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v1/list-of-similar/{self.data.id}/no-hit",
                headers=self._header_builder(),
                timeout=300,
                json={
                    "retryWorkflow": retry_workflow
                }
            )
            raise_for_status_improved(response)


class ListOfSimilarSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=ListOfSimilarSync,
                         retrieve_data_model=ListOfSimilarAPIDTO,
                         create_data_model=CreateListOfSimilar,
                         update_data_model=None,
                         resource="list-of-similar")


class ListOfSimilarAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=ListOfSimilarAsync,
                         retrieve_data_model=ListOfSimilarAPIDTO,
                         create_data_model=CreateListOfSimilar,
                         update_data_model=None,
                         resource="list-of-similar")
