from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from altscore.common.http_errors import raise_for_status_improved
from altscore.cms.helpers import build_headers


class PartnerAPIDTO(BaseModel):
    avatar: Optional[str] = Field(alias="avatar")
    name: str = Field(alias="name")
    short_name: str = Field(alias="shortName")
    partner_id: str = Field(alias="partnerId")
    status: str = Field(alias="status")
    email: str = Field(alias="email")
    legal_name: Optional[str] = Field(alias="legalName", default=None)
    address: Optional[str] = Field(alias="address", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class PartnerBase:

    def __init__(self, base_url):
        self.base_url = base_url


class PartnerAsync(PartnerBase):
    data: PartnerAPIDTO

    def __init__(self, base_url, header_builder, data: PartnerAPIDTO):
        super().__init__(base_url)
        self.base_url = base_url
        self._header_builder = header_builder
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__})"


class PartnerSync(PartnerBase):
    data: PartnerAPIDTO

    def __init__(self, base_url, header_builder, data: PartnerAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.partner_id})"


class PartnersAsyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self, partner_id: Optional[str] = None):
        return build_headers(self, partner_id=partner_id)

    async def me(self) -> PartnerAsync:
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.get(
                "/v2/partners/me",
                # This is important to avoid infinite recursion
                headers=build_headers(self, partner_id=None),
                timeout=120
            )
            raise_for_status_improved(response)
            return PartnerAsync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                data=PartnerAPIDTO.parse_obj(response.json())
            )


class PartnersSyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self, partner_id: Optional[str] = None):
        return build_headers(self, partner_id=partner_id or self.altscore_client.partner_id)

    def me(self) -> PartnerSync:
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.get(
                "/v2/partners/me",
                # This is important to avoid infinite recursion
                headers=build_headers(self, partner_id=None),
                timeout=120
            )
            raise_for_status_improved(response)
            return PartnerSync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                data=PartnerAPIDTO.parse_obj(response.json())
            )
