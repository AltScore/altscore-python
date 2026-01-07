import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class DataModelAPIDTO(BaseModel):
    id: str = Field(alias="id")
    path: str = Field(alias="path")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    entity_type: str = Field(alias="entityType")
    priority: Optional[int] = Field(alias="priority", default=None)
    order: Optional[int] = Field(alias="order", default=None)
    allowed_values: Optional[List[Any]] = Field(alias="allowedValues", default=None)
    data_type: Optional[str] = Field(alias="dataType", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata")
    is_segmentation_field: Optional[bool] = Field(alias="isSegmentationField", default=False)
    is_sensitive: Optional[bool] = Field(alias="isSensitive", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class DataModelCreate(BaseModel):
    path: Optional[str] = Field(alias="path", default="")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    entity_type: str = Field(alias="entityType")
    priority: Optional[int] = Field(alias="priority", default=None)
    allowed_values: Optional[List[Any]] = Field(alias="allowedValues", default=None)
    order: Optional[int] = Field(alias="order", default=None)
    data_type: Optional[str] = Field(alias="dataType", default=None)
    metadata: Optional[dict] = Field(alias="metadata", default={})
    is_segmentation_field: Optional[bool] = Field(alias="isSegmentationField", default=False)
    is_sensitive: Optional[bool] = Field(alias="isSensitive", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class DataModelUpdate(BaseModel):
    path: Optional[str] = Field(alias="path", default="")
    key: Optional[str] = Field(alias="key")
    label: Optional[str] = Field(alias="label")
    priority: Optional[int] = Field(alias="priority", default=None)
    order: Optional[int] = Field(alias="order", default=None)
    allowed_values: Optional[List[Any]] = Field(alias="allowedValues", default=None)
    data_type: Optional[str] = Field(alias="dataType", default=None)
    metadata: Optional[dict] = Field(alias="metadata", default={})
    is_segmentation_field: Optional[bool] = Field(alias="isSegmentationField", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class DataModelSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "data-models", header_builder, renew_token, DataModelAPIDTO.parse_obj(data))


class DataModelAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "data-models", header_builder, renew_token, DataModelAPIDTO.parse_obj(data))


class DataModelSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=DataModelSync, retrieve_data_model=DataModelAPIDTO,
                         create_data_model=DataModelCreate, update_data_model=DataModelUpdate, resource="data-models")

    @retry_on_401
    def make_sensitive(self, data_model_id: str):
        """
        Calls PUT /v1/data-models/{data_model_id}/make-sensitive.
        Returns the updated DataModel resource.
        """
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            resp = client.put(
                f"/v1/data-models/{data_model_id}/make-sensitive",
                headers=self.build_headers(),
                timeout=300,
            )
            raise_for_status_improved(resp)
            return self.sync_resource(
                base_url=self.altscore_client._borrower_central_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=self.retrieve_data_model.parse_obj(resp.json()),
            )


class DataModelAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=DataModelSync, retrieve_data_model=DataModelAPIDTO,
                         create_data_model=DataModelCreate, update_data_model=DataModelUpdate, resource="data-models")

    @retry_on_401_async
    async def make_sensitive(self, data_model_id: str):
        """
        Calls PUT /v1/data-models/{data_model_id}/make-sensitive.
        Returns the updated DataModel resource.
        """
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            resp = await client.put(
                f"/v1/data-models/{data_model_id}/make-sensitive",
                headers=self.build_headers(),
                timeout=300,
            )
            raise_for_status_improved(resp)
            return self.async_resource(
                base_url=self.altscore_client._borrower_central_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=self.retrieve_data_model.parse_obj(resp.json()),
            )
