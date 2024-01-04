from pydantic import BaseModel, Field
from typing import Optional
import httpx
from altscore.common.http_errors import raise_for_status_improved
from altscore.cms.helpers import build_headers
from altscore.cms.model.credit_account import CreditAccountSync, CreditAccountAsync, CreditAccountAPIDTO
import datetime as dt


class ClientAPIDTO(BaseModel):
    id: str = Field(alias="clientId")
    partner_id: str = Field(alias="partnerId")
    status: str = Field(alias="status")
    external_id: str = Field(alias="externalId")
    tax_id: str = Field(alias="taxId")
    email_address: str = Field(alias="emailAddress")
    dba: str = Field(alias="dba")
    legal_name: str = Field(alias="legalName")
    address: str = Field(alias="address")
    phone_number: Optional[str] = Field(alias="phoneNumber", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class CreateClientDTO(BaseModel):
    partner_id: str = Field(alias="partnerId")
    external_id: str = Field(alias="externalId")
    legal_name: str = Field(alias="legalName")
    tax_id: str = Field(alias="taxId")
    dba: str = Field(alias="dba")
    address: str = Field(alias="address")
    email_address: str = Field(alias="emailAddress")
    phone_number: Optional[str] = Field(alias="phoneNumber", default="")
    activation_date: Optional[str] = Field(alias="activationDate", default=dt.date.today().strftime("%Y-%m-%d"))

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class ClientBase:

    def __init__(self, base_url):
        self.base_url = base_url

    def _credit_accounts(
            self, client_id: str, product_family: str
    ) -> (str, Optional[dict]):
        return f"{self.base_url}/v2/clients/{client_id}/credit-accounts/{product_family}"


class ClientAsync(ClientBase):
    data: ClientAPIDTO

    def __init__(self, base_url, header_builder, data: ClientAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.data = data

    async def get_credit_account(self, product_family: str) -> CreditAccountSync:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url = self._credit_accounts(self.data.id, product_family=product_family)
            response = await client.get(
                url,
                headers=self._header_builder()
            )
            return CreditAccountSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=CreditAccountAPIDTO.parse_obj(response.json())
            )

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class ClientSync(ClientBase):
    data: ClientAPIDTO

    def __init__(self, base_url, header_builder, data: ClientAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.data: ClientAPIDTO = data

    def get_credit_account(self, product_family: str) -> CreditAccountSync:
        with httpx.Client(base_url=self.base_url) as client:
            url = self._credit_accounts(self.data.id, product_family=product_family)
            response = client.get(
                url,
                headers=self._header_builder()
            )
            return CreditAccountSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=CreditAccountAPIDTO.parse_obj(response.json())
            )


class ClientsAsyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self, partner_id: Optional[str] = None):
        return build_headers(self, partner_id=partner_id)

    async def create(self, new_entity_data: dict):
        if new_entity_data.get("partnerId") is None:
            new_entity_data["partnerId"] = self.altscore_client.partner_id
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.post(
                "/v2/clients",
                headers=self.build_headers(),
                json=CreateClientDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["clientId"]

    async def retrieve(self, client_identifier: str) -> Optional[ClientAsync]:
        """
        Retrieves a Client Object using a client identifier.
        The identifier can be the clientId, taxId or externalId (needs the X-Partner-Id header)
        """
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.get(
                f"/v2/clients/{client_identifier}",
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return ClientAsync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                data=ClientAPIDTO.parse_obj(response.json())
            )


class ClientsSyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self, partner_id: Optional[str] = None):
        return build_headers(self, partner_id=partner_id or self.altscore_client.partner_id)

    def create(self, new_entity_data: dict):
        if new_entity_data.get("partnerId") is None:
            new_entity_data["partnerId"] = self.altscore_client.partner_id
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.post(
                "/v2/clients",
                headers=self.build_headers(),
                json=CreateClientDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["clientId"]

    def retrieve(self, client_identifier: str) -> Optional[ClientSync]:
        """
        Retrieves a Client Object using a client identifier.
        The identifier can be the clientId, taxId or externalId (needs the X-Partner-Id header)
        """
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.get(
                f"/v2/clients/{client_identifier}",
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return ClientSync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                data=ClientAPIDTO.parse_obj(response.json())
            )
