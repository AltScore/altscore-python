import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class CMSSettingsAPIDTO(BaseModel):
    id: str
    main_partner_id: Optional[str] = Field(alias='mainPartnerId', default=None)
    created_at: str = Field(alias='createdAt')
    updated_at: Optional[str] = Field(None, alias='updatedAt')

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class UpdateCMSSettingsDTO(BaseModel):
    main_partner_id: Optional[str] = Field(alias='mainPartnerId', default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CMSSettingsSync(GenericSyncResource):
    data: CMSSettingsAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "cms-settings", header_builder, renew_token, CMSSettingsAPIDTO.model_validate(data))


class CMSSettingsAsync(GenericAsyncResource):
    data: CMSSettingsAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "cms-settings", header_builder, renew_token, CMSSettingsAPIDTO.model_validate(data))


class CMSSettingsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=CMSSettingsSync,
                         retrieve_data_model=CMSSettingsAPIDTO,
                         create_data_model=None,
                         update_data_model=UpdateCMSSettingsDTO,
                         resource="application/cms-settings")

    @retry_on_401
    def retrieve(self):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                timeout=30
            )
            if response.status_code == 200:
                return self.sync_resource(
                    base_url=self.altscore_client._borrower_central_base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    data=self.retrieve_data_model.model_validate(response.json())
                )
            elif response.status_code in [404]:
                return None

            raise_for_status_improved(response)

    @retry_on_401
    def put(self, put_data: Dict) -> str:
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.put(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                json=self.update_data_model.model_validate(put_data).model_dump(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return self.retrieve_data_model.model_validate(response.json())



class CMSSettingsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=CMSSettingsAsync,
                         retrieve_data_model=CMSSettingsAPIDTO,
                         create_data_model=None,
                         update_data_model=UpdateCMSSettingsDTO,
                         resource="application/cms-settings")


    @retry_on_401_async
    async def retrieve(self):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                timeout=30
            )
            if response.status_code == 200:
                return self.async_resource(
                    base_url=self.altscore_client._borrower_central_base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    data=self.retrieve_data_model.model_validate(response.json())
                )
            elif response.status_code in [404]:
                return None

            raise_for_status_improved(response)

    @retry_on_401_async
    async def put(self, put_data: Dict) -> str:
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.put(
                f"/v1/{self.resource}",
                headers=self.build_headers(),
                json=self.update_data_model.model_validate(put_data).model_dump(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return self.retrieve_data_model.model_validate(response.json())
