from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class IdentityAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")
    label: Optional[str] = Field(alias="label")
    value: Optional[str] = Field(alias="value")
    priority: Optional[int] = Field(alias="priority")
    tags: List[str] = Field(alias="tags")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")
    has_attachments: bool = Field(alias="hasAttachments", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateIdentityDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")
    value: Optional[str] = Field(alias="value")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateIdentityDTO(BaseModel):
    value: Optional[str] = Field(alias="value", default=None)
    tags: Optional[List[str]] = Field(alias="tags", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class IdentitySync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "identities", header_builder, renew_token, IdentityAPIDTO.parse_obj(data))


class IdentityAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "identities", header_builder, renew_token, IdentityAPIDTO.parse_obj(data))


class IdentitiesSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=IdentitySync,
                         retrieve_data_model=IdentityAPIDTO,
                         create_data_model=CreateIdentityDTO,
                         update_data_model=UpdateIdentityDTO,
                         resource="identities")


class IdentitiesAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=IdentityAsync,
                         retrieve_data_model=IdentityAPIDTO,
                         create_data_model=CreateIdentityDTO,
                         update_data_model=UpdateIdentityDTO,
                         resource="identities")
