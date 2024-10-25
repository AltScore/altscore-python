from pydantic import BaseModel, Field
from typing import Optional, List
import httpx

from altscore.cms.model.disbursement_accounts import CreateDisbursementClientAccountDTO, BankAccount, \
    DisbursementClientAccountAPIDTO
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.cms.model.credit_accounts import CreditAccountSync, CreditAccountAsync, CreditAccountAPIDTO
from altscore.cms.model.payment_accounts import PaymentAccountAPIDTO, CreatePaymentAccountDTO, \
    CreatePaymentReferenceDTO, Reference
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
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

    @staticmethod
    def _credit_accounts(
            client_id: str, product_family: str
    ) -> (str, Optional[dict]):
        return f"/v2/clients/{client_id}/credit-accounts/{product_family}"

    @staticmethod
    def _status(client_id: str):
        return f"/v2/clients/{client_id}/status"

    @staticmethod
    def _get_payments_accounts(client_id: str):
        return f"/v1/payments/accounts/{client_id}"

    @staticmethod
    def _create_payment_account():
        return f"/v1/payments/accounts"

    @staticmethod
    def _create_payment_reference(client_id: str):
        return f"/v1/payments/accounts/{client_id}/references"

# TODO for future use for cancel reference
    @staticmethod
    def _cancel_payment_reference(client_id: str, reference_id: str):
        return f"/v1/payments/accounts/{client_id}/references{reference_id}/cancellation"

    @staticmethod
    def _create_disbursement_account(country: str):
        return f"/v1/disbursements/accounts/{country}/client"

    @staticmethod
    def _get_disbursement_account(country: str, client_id: str):
        return f"/v1/disbursements/accounts/{country}/client/{client_id}"


class ClientAsync(ClientBase):
    data: ClientAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: ClientAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    @retry_on_401_async
    async def get_credit_account(self, product_family: str) -> CreditAccountAsync:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._credit_accounts(self.data.id, product_family=product_family),
                headers=self._header_builder(partner_id=self.data.partner_id),
                timeout=30
            )
            return CreditAccountAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                renew_token=self.renew_token,
                data=CreditAccountAPIDTO.parse_obj(response.json())
            )

    @retry_on_401_async
    async def enable(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.put(
                self._status(self.data.id),
                json={
                    "status": "enabled"
                },
                timeout=30,
                headers=self._header_builder(partner_id=self.data.partner_id)
            )
            raise_for_status_improved(response)
            self.data = ClientAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def disable(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.put(
                self._status(self.data.id),
                json={
                    "status": "disabled"
                },
                timeout=30,
                headers=self._header_builder(partner_id=self.data.partner_id)
            )
            raise_for_status_improved(response)
            self.data = ClientAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def get_payment_accounts(self) -> Optional[PaymentAccountAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._get_payments_accounts(self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                timeout=30
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return PaymentAccountAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def create_payment_account(self, auto_create_references: bool = True) -> PaymentAccountAPIDTO:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._create_payment_account(),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreatePaymentAccountDTO.parse_obj({
                    "partner_id": self.data.partner_id,
                    "client_id": self.data.id,
                    "auto_create_references": auto_create_references
                }).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return PaymentAccountAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def create_payment_reference(self, provider: str = None) -> List[Reference]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._create_payment_reference(self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreatePaymentReferenceDTO.parse_obj({
                    "provider": provider
                }).dict(by_alias=True, exclude_none=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Reference.parse_obj(e) for e in response.json()]

    @retry_on_401_async
    async def create_disbursement_account(self,bank_account :dict,country: str):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._create_disbursement_account(country),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreateDisbursementClientAccountDTO.parse_obj({
                    "id": self.data.id,
                    "partnerId":self.data.partner_id,
                    "email": self.data.email_address,
                    "phone": self.data.phone_number,
                    "bankAccount": BankAccount.parse_obj(bank_account).dict(by_alias=True,exclude_none=True),
                }).dict(by_alias=True, exclude_none=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return DisbursementClientAccountAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def get_disbursement_account(self, country: str) -> Optional[DisbursementClientAccountAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._get_disbursement_account(country, self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                timeout=30
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return DisbursementClientAccountAPIDTO.parse_obj(response.json())

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class ClientSync(ClientBase):
    data: ClientAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: ClientAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data: ClientAPIDTO = data

    @retry_on_401
    def get_credit_account(self, product_family: str) -> CreditAccountSync:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._credit_accounts(self.data.id, product_family=product_family),
                headers=self._header_builder(partner_id=self.data.partner_id)
            )
            return CreditAccountSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                renew_token=self.renew_token,
                data=CreditAccountAPIDTO.parse_obj(response.json())
            )

    @retry_on_401
    def enable(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.put(
                self._status(self.data.id),
                json={
                    "status": "enabled"
                },
                timeout=30,
                headers=self._header_builder(partner_id=self.data.partner_id)
            )
            raise_for_status_improved(response)
            self.data = ClientAPIDTO.parse_obj(response.json())

    @retry_on_401
    def disable(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.put(
                self._status(self.data.id),
                json={
                    "status": "disabled"
                },
                timeout=30,
                headers=self._header_builder(partner_id=self.data.partner_id)
            )
            raise_for_status_improved(response)
            self.data = ClientAPIDTO.parse_obj(response.json())

    @retry_on_401
    def get_payment_accounts(self) -> Optional[PaymentAccountAPIDTO]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._get_payments_accounts(self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                timeout=30
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return PaymentAccountAPIDTO.parse_obj(response.json())

    @retry_on_401
    def create_payment_account(self, auto_create_references: bool = True) -> PaymentAccountAPIDTO:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._create_payment_account(),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreatePaymentAccountDTO.parse_obj({
                    "partner_id": self.data.partner_id,
                    "client_id": self.data.id,
                    "auto_create_references": auto_create_references
                }).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return PaymentAccountAPIDTO.parse_obj(response.json())

    @retry_on_401
    def create_payment_reference(self, provider: str = None) -> List[Reference]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._create_payment_reference(self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreatePaymentReferenceDTO.parse_obj({
                    "provider": provider
                }).dict(by_alias=True, exclude_none=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Reference.parse_obj(e) for e in response.json()]

    @retry_on_401
    def create_disbursement_account(self,  country: str, bank_account: dict,):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._create_disbursement_account(country),
                headers=self._header_builder(partner_id=self.data.partner_id),
                json=CreateDisbursementClientAccountDTO.parse_obj({
                    "id": self.data.id,
                    "partnerId": self.data.partner_id,
                    "email": self.data.email_address,
                    "phone": self.data.phone_number,
                    "bankAccount": BankAccount.parse_obj(bank_account).dict(by_alias=True, exclude_none=True),
                }).dict(by_alias=True, exclude_none=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return DisbursementClientAccountAPIDTO.parse_obj(response.json())

    @retry_on_401
    def get_disbursement_account(self, country: str) -> Optional[DisbursementClientAccountAPIDTO]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._get_disbursement_account(country, self.data.id),
                headers=self._header_builder(partner_id=self.data.partner_id),
                timeout=30
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return DisbursementClientAccountAPIDTO.parse_obj(response.json())

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class ClientsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            async_resource=ClientAsync,
            retrieve_data_model=ClientAPIDTO,
            create_data_model=CreateClientDTO,
            update_data_model=None,
            resource="clients",
            resource_version="v2"
        )

    def renew_token(self):
        self.altscore_client.renew_token()

    @retry_on_401_async
    async def retrieve_by_external_id(self, external_id: str, partner_id: str = None) -> Optional[ClientAsync]:
        headers = self.build_headers()
        if partner_id is not None:
            headers["x-partner-id"] = partner_id

        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.get(
                f"/{self.resource_version}/{self.resource}/{external_id}",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                return self.async_resource(
                    base_url=self.altscore_client._cms_base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    data=self.retrieve_data_model.parse_obj(response.json())
                )
            return None

    @retry_on_401_async
    async def create(self, new_entity_data: dict):
        partner_id = new_entity_data.get("partnerId")
        if partner_id is None:
            partner_id = self.altscore_client.partner_id
            new_entity_data["partnerId"] = partner_id

        headers = self.build_headers()
        # if this is a client creation with "impersonation" of a partner we need to set the x-partner-id header
        headers["x-partner-id"] = partner_id
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.post(
                "/v2/clients",
                headers=headers,
                json=CreateClientDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["clientId"]


class ClientsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            sync_resource=ClientSync,
            retrieve_data_model=ClientAPIDTO,
            create_data_model=CreateClientDTO,
            update_data_model=None,
            resource="clients",
            resource_version="v2"
        )

    def renew_token(self):
        self.altscore_client.renew_token()

    @retry_on_401
    def retrieve_by_external_id(self, external_id: str, partner_id: str = None) -> Optional[ClientSync]:

        headers = self.build_headers()
        if partner_id is not None:
            headers["x-partner-id"] = partner_id

        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.get(
                f"/{self.resource_version}/{self.resource}/{external_id}",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                return self.sync_resource(
                    base_url=self.altscore_client._cms_base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    data=self.retrieve_data_model.parse_obj(response.json())
                )
            return None

    @retry_on_401
    def create(self, new_entity_data: dict):
        partner_id = new_entity_data.get("partnerId")
        if partner_id is None:
            partner_id = self.altscore_client.partner_id
            new_entity_data["partnerId"] = partner_id

        headers = self.build_headers()
        # if this is a client creation with "impersonation" of a partner we need to set the x-partner-id header
        headers["x-partner-id"] = partner_id
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.post(
                "/v2/clients",
                headers=headers,
                json=CreateClientDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["clientId"]