from pydantic import BaseModel, Field
from typing import Optional, Dict
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class AlertAPIDTO(BaseModel):
    id: str = Field(alias="id")
    rule_id: str = Field(alias="ruleId")
    rule_code: Optional[str] = Field(alias="ruleCode", default=None)
    borrower_id: str = Field(alias="borrowerId")
    level: int = Field(alias="level")
    message: str = Field(alias="message")
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    is_dismissed: bool = Field(alias="isDismissed")
    dismissed_by: Optional[str] = Field(alias="dismissedBy")
    dismissed_at: Optional[str] = Field(alias="dismissedAt")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateAlert(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    rule_id: str = Field(alias="ruleId")
    rule_code: Optional[str] = Field(alias="ruleCode", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    level: int = Field(alias="level")
    message: str = Field(alias="message")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class DismissAlert(BaseModel):
    dismissed_by: str = Field(alias="dismissedBy")
    dismissed_at: Optional[str] = Field(alias="dismissedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class AlertSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "alerts", header_builder, renew_token, AlertAPIDTO.parse_obj(data))

    @retry_on_401
    def dismiss(self, dismissed_by: str, dismissed_at: Optional[str] = None) -> str:
        with httpx.Client(base_url=self.base_url._borrower_central_base_url) as client:
            data = DismissAlert(dismissed_by=dismissed_by, dismissed_at=dismissed_at).dict(by_alias=True)
            response = client.put(
                f"{self.resource}/{self.data.id}/dismiss",
                json=data,
                headers=self._header_builder(),
            )
            raise_for_status_improved(response)
            return self.data.id


class AlertAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "alerts", header_builder, renew_token, AlertAPIDTO.parse_obj(data))

    @retry_on_401_async
    async def dismiss(self, dismissed_by: str, dismissed_at: Optional[str] = None) -> str:
        async with httpx.AsyncClient(base_url=self.base_url._borrower_central_base_url) as client:
            data = DismissAlert(dismissed_by=dismissed_by, dismissed_at=dismissed_at).dict(by_alias=True)
            response = await client.put(
                f"{self.resource}/{self.data.id}/dismiss",
                json=data,
                headers=self._header_builder(),
            )
            raise_for_status_improved(response)
            return self.data.id


class AlertsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=AlertSync,
                         retrieve_data_model=AlertAPIDTO,
                         create_data_model=CreateAlert,
                         update_data_model=None,
                         resource="alerts")


class AlertsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=AlertAsync,
                         retrieve_data_model=AlertAPIDTO,
                         create_data_model=CreateAlert,
                         update_data_model=None,
                         resource="alerts")
