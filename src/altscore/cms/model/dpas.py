from pydantic import BaseModel, Field
from typing import List
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
from altscore.cms.model.common import Money, Schedule, Terms
import datetime as dt
from dateutil.parser import parse as date_parser


class Client(BaseModel):
    id: str = Field(alias="clientId")
    partner_id: str = Field(alias="partnerId")
    external_id: str = Field(alias="externalId")
    email: str = Field(alias="email")
    legal_name: str = Field(alias="legalName")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPAFlowAPIDTO(BaseModel):
    id: str = Field(alias="flowId")
    tenant: str = Field(alias="tenant")
    reference_id: str = Field(alias="referenceId")
    status: str = Field(alias="status")
    client: Client = Field(alias="client")
    schedule: Schedule = Field(alias="schedule")
    terms: Terms = Field(alias="terms")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class CreateDPAFlowDTO(BaseModel):
    amount: Money = Field(alias="amount")
    disbursement_date: str = Field(alias="disbursementDate")
    external_id: str = Field(alias="externalId")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class InvoiceInstallment(BaseModel):
    due_date: str = Field(alias="dueDate")
    number: int = Field(alias="number")
    interest: Money = Field(alias="interest")
    amount: Money = Field(alias="amount")
    tax: Money = Field(alias="tax")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Invoice(BaseModel):
    amount: Money = Field(alias="amount")
    invoice_date: str = Field(alias="invoiceDate")
    installments: List[InvoiceInstallment] = Field(alias="installments")
    notes: str = Field(alias="notes")
    reference_id: str = Field(alias="referenceId")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPABase:

    @staticmethod
    def _approval(flow_id: str):
        return f"/v1/dpas/{flow_id}/approval"

    @staticmethod
    def _cancellation(flow_id: str):
        return f"/v1/dpas/{flow_id}/cancellation"

    @staticmethod
    def _invoice(flow_id: str):
        return f"/v1/dpas/{flow_id}/invoices"


class DPAFlowAsync(DPABase):
    data: DPAFlowAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DPAFlowAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    @retry_on_401_async
    async def approve(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._approval(self.data.id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def cancel(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._cancellation(self.data.id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    @retry_on_401_async
    async def submit_invoice(self, invoice: dict):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._invoice(self.data.id),
                json=Invoice.parse_obj(invoice).dict(by_alias=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class DPAFlowSync(DPABase):
    data: DPAFlowAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DPAFlowAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data: DPAFlowAPIDTO = data

    @retry_on_401
    def approve(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._approval(self.data.id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    @retry_on_401
    def cancel(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._cancellation(self.data.id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class DPAFlowsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            async_resource=DPAFlowAsync,
            retrieve_data_model=DPAFlowAPIDTO,
            create_data_model=CreateDPAFlowDTO,
            update_data_model=None,
            resource="dpas"
        )

    @retry_on_401_async
    async def create(self, new_entity_data: dict):
        disbursement_date_str = \
            new_entity_data.get("disbursementDate") or new_entity_data.get("disbursement_date")
        if disbursement_date_str is None:
            disbursement_date = dt.date.today().strftime("%Y-%m-%d")
        else:
            disbursement_date = date_parser(disbursement_date_str).strftime("%Y-%m-%d")
        new_entity_data["disbursementDate"] = disbursement_date

        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.post(
                f"/{self.resource_version}/{self.resource}",
                headers=self.build_headers(),
                json=self.create_data_model.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return self.retrieve_data_model.parse_obj(response.json()).id


class DPAFlowsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            sync_resource=DPAFlowSync,
            retrieve_data_model=DPAFlowAPIDTO,
            create_data_model=CreateDPAFlowDTO,
            update_data_model=None,
            resource="dpas"
        )

    @retry_on_401
    def create(self, new_entity_data: dict):
        disbursement_date_str = \
            new_entity_data.get("disbursementDate") or new_entity_data.get("disbursement_date")
        if disbursement_date_str is None:
            disbursement_date = dt.date.today().strftime("%Y-%m-%d")
        else:
            disbursement_date = date_parser(disbursement_date_str).strftime("%Y-%m-%d")
        new_entity_data["disbursementDate"] = disbursement_date

        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.post(
                f"/{self.resource_version}/{self.resource}",
                headers=self.build_headers(),
                json=self.create_data_model.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return self.retrieve_data_model.parse_obj(response.json()).id
