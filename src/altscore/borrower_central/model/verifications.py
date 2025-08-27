import base64

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class VerificationsAPIDTO(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerId")
    verification_id: Optional[str] = Field(alias="verificationId", default=None)
    provider: str = Field(alias="provider")
    provider_verification_key: str = Field(
        alias="providerVerificationKey")
    provider_verification_id: str = Field(
        alias="providerVerificationId")
    identity_id: str = Field(alias="identityId")
    has_attachments: bool = Field(alias="hasAttachments", default=None)
    verification_request_payload: Dict = Field(alias="verificationRequestPayload",
                                               default={})
    status: str = Field(alias="status")
    validated_at: Optional[str] = Field(alias="validatedAt")
    expires_at: Optional[str] = Field(alias="expiresAt")
    updated_at: Optional[str] = Field(alias="updatedAt")
    created_at: str = Field(alias="createdAt")
    is_consumed_by_signature: bool = Field(alias="isConsumedBySignature", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateVerificationSchema(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    provider: str = Field(alias="provider")
    identity_key: str = Field(alias="identityKey")
    status: Optional[str] = Field(alias="status", default="pending")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CheckVerificationSchema(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    provider: str = Field(alias="provider")
    identities_key: Optional[List[str]] = Field(alias="identitiesKey", default=None)
    video_url: Optional[str] = Field(default=None, alias="videoUrl")
    video_base64: Optional[str] = Field(default=None, alias="videoBase64")

    @validator('video_base64')
    def validate_base64(cls, v):
        if v is not None:
            try:
                base64.b64decode(v)
            except Exception:
                raise ValueError('Invalid base64 format')
        return v

    @validator('video_base64')
    def validate_video_input(cls, v, values):
        video_url = values.get('video_url')
        video_base64 = v

        if not video_url and not video_base64:
            raise ValueError('Debe proporcionar video_url o video_base64')

        if video_url and video_base64:
            raise ValueError('Proporcione solo video_url O video_base64, no ambos')

        return v

    @property
    def video_input(self) -> Union[str, bytes]:
        if self.video_url:
            return self.video_url
        elif self.video_base64:
            return base64.b64decode(self.video_base64)
        else:
            raise ValueError("No video input provided")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class VerificationsSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/verifications", header_builder, renew_token,
                         VerificationsAPIDTO.parse_obj(data))


class VerificationsAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/verifications", header_builder, renew_token,
                         VerificationsAPIDTO.parse_obj(data))


class VerificationsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=VerificationsSync,
                         retrieve_data_model=VerificationsAPIDTO,
                         create_data_model=CreateVerificationSchema,
                         update_data_model=CreateVerificationSchema,
                         resource="/verifications")

    @retry_on_401
    def create_verification(self, request_body: Dict[str, Any]):
        request_data = CreateVerificationSchema(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/verifications",
                json=request_data.dict(by_alias=True),
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    def retrieve_by_id(self, verification_id: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.get(
                f"/v1/verifications/{verification_id}",
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    def retrieve_all(self):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.get(
                f"/v1/verifications",
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    def attempt(self, verification_id: str, request_body: Dict[str, Any]):
        request_data = CheckVerificationSchema(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/verifications/{verification_id}/attempt",
                headers=self.build_headers(),
                json=request_data.dict(by_alias=True),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

class VerificationsASyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=VerificationsAsync,
                         retrieve_data_model=VerificationsAPIDTO,
                         create_data_model=CreateVerificationSchema,
                         update_data_model=CreateVerificationSchema,
                         resource="/verifications")

    @retry_on_401
    async def create_verification(self, request_body: Dict[str, Any]):
        request_data = CreateVerificationSchema(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/verifications",
                json=request_data.dict(by_alias=True),
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    async def retrieve_by_id(self, verification_id: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.get(
                f"/v1/verifications/{verification_id}",
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    async def retrieve_all(self):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.get(
                f"/v1/verifications",
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()

    @retry_on_401
    async def attempt(self, verification_id: str, request_body: Dict[str, Any]):
        request_data = CheckVerificationSchema(
            **request_body
        )
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            request = client.post(
                f"/v1/verifications/{verification_id}/attempt",
                headers=self.build_headers(),
                json=request_data.dict(by_alias=True),
                timeout=120,
            )
            raise_for_status_improved(request)
            return request.json()
