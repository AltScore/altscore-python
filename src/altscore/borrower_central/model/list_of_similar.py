import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule

class ListStatus:
    PENDING = "pending"
    APPLIED = "applied"
    NO_HIT = "no_hit"

class SimilarEntity(BaseModel):
    entity_type: str = Field(alias="entityType")
    key: str = Field(alias="key")
    proposed_value: Any = Field(alias="proposedValue")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class Similar(BaseModel):
    label: str = Field(alias="label")
    description: Optional[str] = Field(alias="description")
    entities: List[SimilarEntity] = Field(alias="entities")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ListOfSimilarAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    deal_id: Optional[str] = Field(alias="dealId", default=None)
    execution_id: Optional[str] = Field(alias="executionId")
    list_of_similar: List[Similar] = Field(alias="listOfSimilar")
    max_selections: int = Field(alias="maxSelections", default=1)
    selection_keys: Optional[Dict[str, List[str]]] = Field(alias="selectionKeys", default=None)
    status: Optional[str] = Field(alias="status")
    applied_index: Optional[int] = Field(alias="appliedIndex", default=None)
    applied_indexes: Optional[List[int]] = Field(alias="appliedIndexes", default=None)
    applied_by: Optional[str] = Field(alias="appliedBy")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateListOfSimilar(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    deal_id: Optional[str] = Field(alias="dealId", default=None)
    execution_id: Optional[str] = Field(alias="executionId")
    list_of_similar: List[Similar] = Field(alias="listOfSimilar")
    # Ordered multi-pick: how many similars the operator may pick, and the key each pick
    # position writes per entity key, e.g. {"paynetId": ["paynetId", "paynetId2", "paynetId3"]}.
    # An entity key with no entry is written for the first pick only.
    max_selections: int = Field(alias="maxSelections", default=1)
    selection_keys: Optional[Dict[str, List[str]]] = Field(alias="selectionKeys", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


def _apply_payload(index: Optional[int], indexes: Optional[List[int]], retry_workflow: bool) -> Dict[str, Any]:
    """One pick as `index` or an ordered multi-pick as `indexes`; exactly one of the two."""
    if (index is None) == (indexes is None):
        raise ValueError("pass exactly one of 'index' or 'indexes'")
    payload: Dict[str, Any] = {"retryWorkflow": retry_workflow}
    if indexes is not None:
        payload["indexes"] = list(indexes)
    else:
        payload["index"] = index
    return payload


class ListOfSimilarSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "list-of-similar", header_builder, renew_token, ListOfSimilarAPIDTO.parse_obj(data))

    @retry_on_401
    def apply(self, index: Optional[int] = None, retry_workflow: bool = False,
              indexes: Optional[List[int]] = None):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v1/list-of-similar/{self.data.id}/apply",
                headers=self._header_builder(),
                timeout=300,
                json=_apply_payload(index, indexes, retry_workflow)
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
        super().__init__(base_url, "list-of-similar", header_builder, renew_token, ListOfSimilarAPIDTO.parse_obj(data))

    @retry_on_401_async
    async def apply(self, index: Optional[int] = None, retry_workflow: bool = False,
                    indexes: Optional[List[int]] = None):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v1/list-of-similar/{self.data.id}/apply",
                headers=self._header_builder(),
                timeout=300,
                json=_apply_payload(index, indexes, retry_workflow)
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
