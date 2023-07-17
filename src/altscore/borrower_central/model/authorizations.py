from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class AuthorizationAPIDTO(BaseModel):
    id: str = Field(alias="ID")
    tenant: str = Field(alias="tenant")
    form_id: Optional[str] = Field(alias="formID")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    borrower_id: Optional[str] = Field(alias="borrowerID")
    expires_at: Optional[str] = Field(alias="expiresAt")
    ip_address: Optional[str] = Field(alias="ipAddress")
    policy_link: Optional[str] = Field(alias="policyLink")
    external_id: Optional[str] = Field(alias="externalID", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    authorized_at: Optional[str] = Field(alias="authorizedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")
    has_attachments: bool = Field(alias="hasAttachments", default=False)
    has_signatures: bool = Field(alias="hasSignatures", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True



class CreateAuthorizationDTO(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerID", default=None)
    form_id: Optional[str] = Field(alias="formID", default=None)
    ip_address: Optional[str] = Field(alias="ipAddress", default=None, hidden=True)
    key: str = Field(alias="key")
    policy_link: Optional[str] = Field(alias="policyLink")
    external_id: Optional[str] = Field(alias="externalID")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class AuthorizationSync(GenericSyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, AuthorizationAPIDTO.parse_obj(data))


class AuthorizationAsync(GenericAsyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, AuthorizationAPIDTO.parse_obj(data))


class AuthorizationsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=AuthorizationSync,
                         retrieve_data_model=AuthorizationAPIDTO,
                         create_data_model=CreateAuthorizationDTO,
                         update_data_model=None,
                         resource="authorizations")


class AuthorizationsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=AuthorizationAsync,
                         retrieve_data_model=AuthorizationAPIDTO,
                         create_data_model=CreateAuthorizationDTO,
                         update_data_model=None,
                         resource="authorizations")
