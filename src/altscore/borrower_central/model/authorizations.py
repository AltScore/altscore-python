from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class AuthorizationAPIDTO(BaseModel):
    id: str = Field(alias="id")
    tenant: str = Field(alias="tenant")
    form_id: Optional[str] = Field(None, alias="formId")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    borrower_id: Optional[str] = Field(None, alias="borrowerId")
    expires_at: Optional[str] = Field(None, alias="expiresAt")
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    policy_link: Optional[str] = Field(None, alias="policyLink")
    external_id: Optional[str] = Field(alias="externalId", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    authorized_at: Optional[str] = Field(None, alias="authorizedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    has_attachments: bool = Field(alias="hasAttachments", default=False)
    has_signatures: bool = Field(alias="hasSignatures", default=False)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }



class CreateAuthorizationDTO(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    form_id: Optional[str] = Field(alias="formId", default=None)
    ip_address: Optional[str] = Field(alias="ipAddress", default=None)
    key: str = Field(alias="key")
    policy_link: Optional[str] = Field(None, alias="policyLink")
    external_id: Optional[str] = Field(None, alias="externalId")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    tags: List[str] = Field(alias="tags", default=[])

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class AuthorizationSync(GenericSyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, renew_token, AuthorizationAPIDTO.model_validate(data))


class AuthorizationAsync(GenericAsyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, renew_token, AuthorizationAPIDTO.model_validate(data))


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
