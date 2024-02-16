from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
from altscore.cms.model.common import Money, Schedule, Terms

import datetime as dt


class Balance(BaseModel):
    fees: Money = Field(alias="fees")
    interest: Money = Field(alias="interest")
    principal: Money = Field(alias="principal")
    taxes: Money = Field(alias="taxes")
    penalties: Money = Field(alias="penalties")
    total: Money = Field(alias="total")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


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


class Transaction(BaseModel):
    id: str = Field(alias="transactionId")
    breakdown: List[Balance] = Field(alias="breakdown")
    amount: Money = Field(alias="amount")
    type: str = Field(alias="type")
    date: str = Field(alias="date")
    reference_id: str = Field(alias="referenceId", default=None)
    notes: Optional[str] = Field(alias="notes", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DebtAPIDTO(BaseModel):
    id: str = Field(alias="debtId")
    flow_id: str = Field(alias="flowId")
    tenant: str = Field(alias="tenant")
    reference_id: str = Field(alias="referenceId")
    status: str = Field(alias="status")
    client: Client = Field(alias="client")
    balance: Balance = Field(alias="balance")
    schedule: List[Schedule] = Field(alias="schedule")
    terms: Terms = Field(alias="terms")
    transactions: List[Transaction] = Field(alias="transactions")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Payment(BaseModel):
    debt_id: str = Field(alias="debtId")
    amount: Money = Field(alias="amount")
    payment_date: str = Field(alias="paymentDate")
    reference_id: str = Field(alias="referenceId")
    notes: Optional[str] = Field(alias="notes")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class PenaltyBalance(BaseModel):
    fees: Money = Field(alias="fees")
    interest: Money = Field(alias="interest")
    principal: Money = Field(alias="principal")
    taxes: Money = Field(alias="taxes")
    penalties: Money = Field(alias="penalties")
    total: Money = Field(alias="total")
    installment: int = Field(alias="installment")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Penalty(BaseModel):
    amount: Money = Field(alias="amount")
    breakdown: List[PenaltyBalance] = Field(alias="breakdown")
    date: str = Field(alias="date")
    notes: Optional[str] = Field(alias="notes")
    reference_id: str = Field(alias="referenceId")
    transaction_id: str = Field(alias="transactionId")
    type: str = Field(alias="type")


class DebtBase:

    @staticmethod
    def _payments(flow_id: str):
        return f"/v1/dpas/{flow_id}/payments"

    @staticmethod
    def _penalties(flow_id: str):
        return f"/v1/dpas/{flow_id}/penalties"


class DebtAsync(DebtBase):
    data: DebtAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DebtAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    @retry_on_401_async
    async def get_payments(self) -> List[Payment]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._payments(self.data.flow_id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Payment.parse_obj(e) for e in response.json()]

    @retry_on_401_async
    async def submit_payment(self, amount: str, currency: str, reference_id: str, notes: Optional[str] = None,
                             payment_date: Optional[dt.date] = None) -> None:
        if payment_date is None:
            payment_date = dt.date.today()
        if notes is None:
            notes = ""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._payments(self.data.flow_id),
                json={
                    "amount": {
                        "amount": amount,
                        "currency": currency
                    },
                    "referenceId": reference_id,
                    "notes": notes,
                    "paymentDate": payment_date.strftime("%Y-%m-%d")
                },
                timeout=30,
                headers=self._header_builder()
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_penalties(self) -> List[Penalty]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._penalties(self.data.flow_id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Penalty.parse_obj(e) for e in response.json()]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class DebtSync(DebtBase):
    data: DebtAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DebtAPIDTO):
        super().__init__()
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    @retry_on_401
    def get_payments(self) -> List[Payment]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._payments(self.data.flow_id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Payment.parse_obj(e) for e in response.json()]

    @retry_on_401
    def submit_payment(self, amount: str, currency: str, reference_id: str, notes: Optional[str] = None,
                       payment_date: Optional[dt.date] = None) -> None:
        if payment_date is None:
            payment_date = dt.date.today()
        if notes is None:
            notes = ""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._payments(self.data.flow_id),
                json={
                    "amount": {
                        "amount": amount,
                        "currency": currency
                    },
                    "referenceId": reference_id,
                    "notes": notes,
                    "paymentDate": payment_date.strftime("%Y-%m-%d")
                },
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401
    def get_penalties(self) -> List[Penalty]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._penalties(self.data.flow_id),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [Penalty.parse_obj(e) for e in response.json()]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class DebtsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            async_resource=DebtAsync,
            retrieve_data_model=DebtAPIDTO,
            create_data_model=None,
            update_data_model=None,
            resource="debts"
        )


class DebtsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            sync_resource=DebtSync,
            retrieve_data_model=DebtAPIDTO,
            create_data_model=None,
            update_data_model=None,
            resource="debts"
        )
