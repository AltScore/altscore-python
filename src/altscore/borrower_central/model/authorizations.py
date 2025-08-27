import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

from altscore.common.http_errors import raise_for_status_improved, retry_on_401
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule

class DocumentRequest(BaseModel):
    filename: str = Field(alias="filename")
    media_type: str = Field(alias="mediaType")
    url: Optional[str] = Field(alias="url", default=None)
    base64: Optional[str] = Field(alias="base64", default=None)
    page: Optional[int] = Field(alias="page", default=0)
    posX: Optional[float] = Field(alias="posX", default=50)
    posY: Optional[float] = Field(alias="posY", default=50)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class VerificationRequest(BaseModel):
    verification_id: str = Field(alias="verificationId")
    provider: str = Field(alias="provider")
    documents: List[DocumentRequest] = Field(alias="documents")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class AuthorizationAPIDTO(BaseModel):
    id: str = Field(alias="id")
    tenant: str = Field(alias="tenant")
    form_id: Optional[str] = Field(alias="formId")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    borrower_id: Optional[str] = Field(alias="borrowerId")
    expires_at: Optional[str] = Field(alias="expiresAt")
    ip_address: Optional[str] = Field(alias="ipAddress")
    policy_link: Optional[str] = Field(alias="policyLink")
    external_id: Optional[str] = Field(alias="externalId", default=None)
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
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    form_id: Optional[str] = Field(alias="formId", default=None)
    ip_address: Optional[str] = Field(alias="ipAddress", default=None, hidden=True)
    key: str = Field(alias="key")
    policy_link: Optional[str] = Field(alias="policyLink")
    external_id: Optional[str] = Field(alias="externalId")
    identity_key: str = Field(alias="identityKey")
    identity_value: str = Field(alias="identityValue")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class AuthorizationSync(GenericSyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, renew_token, AuthorizationAPIDTO.parse_obj(data))


class AuthorizationAsync(GenericAsyncResource):
    data: AuthorizationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "authorizations", header_builder, renew_token, AuthorizationAPIDTO.parse_obj(data))


class AuthorizationsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=AuthorizationSync,
                         retrieve_data_model=AuthorizationAPIDTO,
                         create_data_model=CreateAuthorizationDTO,
                         update_data_model=None,
                         resource="authorizations")

    @retry_on_401
    def sign_with_verification(self, authorization_id: str, request_body: Dict[str, Any]):
        request_data = VerificationRequest(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/authorizations/{authorization_id}/sign-with-verification",
                json=request_data.dict(by_alias=True),
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()


class AuthorizationsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=AuthorizationAsync,
                         retrieve_data_model=AuthorizationAPIDTO,
                         create_data_model=CreateAuthorizationDTO,
                         update_data_model=None,
                         resource="authorizations")


    @retry_on_401
    async def sign_with_verification(self, authorization_id: str, request_body: Dict[str, Any]):
        request_data = VerificationRequest(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/authorizations/{authorization_id}/sign-with-verification",
                json=request_data.dict(by_alias=True),
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()
