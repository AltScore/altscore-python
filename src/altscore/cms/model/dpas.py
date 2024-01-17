from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from altscore.common.http_errors import raise_for_status_improved
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
from altscore.cms.model.common import Money, Schedule, Terms
import datetime as dt


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

    def __init__(self, base_url, header_builder, data: DPAFlowAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.data = data

    async def approve(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._approval(self.data.id),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    async def cancel(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._cancellation(self.data.id),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    async def submit_invoice(self, invoice: dict):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._invoice(self.data.id),
                json=Invoice.parse_obj(invoice).dict(by_alias=True),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            return response.json()

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class DPAFlowSync(DPABase):
    data: DPAFlowAPIDTO

    def __init__(self, base_url, header_builder, data: DPAFlowAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.data: DPAFlowAPIDTO = data

    def approve(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._approval(self.data.id),
                headers=self._header_builder()
            )
            raise_for_status_improved(response)
            self.data = DPAFlowAPIDTO.parse_obj(response.json())

    def cancel(self):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._cancellation(self.data.id),
                headers=self._header_builder()
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

    async def create(self, amount: str, currency: str, external_id: str,
                     disbursement_date: Optional[dt.date] = None) -> str:
        if disbursement_date is None:
            disbursement_date = dt.date.today()
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.post(
                "/v1/dpas",
                json=CreateDPAFlowDTO.parse_obj(
                    {
                        "amount": {
                            "amount": amount,
                            "currency": currency
                        },
                        "externalId": external_id,
                        "disbursementDate": disbursement_date.strftime("%Y-%m-%d")
                    }
                ).dict(by_alias=True),
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return response.json()["flowId"]


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

    def create(self, amount: str, currency: str, external_id: str,
               disbursement_date: Optional[dt.date] = None) -> str:
        if disbursement_date is None:
            disbursement_date = dt.date.today()
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.post(
                "/v1/dpas",
                json=CreateDPAFlowDTO.parse_obj(
                    {
                        "amount": {
                            "amount": amount,
                            "currency": currency
                        },
                        "externalId": external_id,
                        "disbursementDate": disbursement_date.strftime("%Y-%m-%d")
                    }
                ).dict(by_alias=True),
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return response.json()["flowId"]
