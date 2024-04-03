from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
from altscore.cms.helpers import build_headers


class PartnerAPIDTO(BaseModel):
    id: str = Field(alias="partnerId")
    avatar: Optional[str] = Field(alias="avatar", default="")
    name: str = Field(alias="name")
    short_name: str = Field(alias="shortName")
    partner_id: str = Field(alias="partnerId")
    status: str = Field(alias="status")
    is_aggregator: bool = Field(alias="isAggregator")
    email: str = Field(alias="email")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class CreatePartnerDTO(BaseModel):
    name: str = Field(alias="name")
    short_name: str = Field(alias="shortName")
    email: str = Field(alias="email")
    tax_id: str = Field(alias="taxId")
    is_aggregator: Optional[bool] = Field(alias="isAggregator", default=False)
    avatar: Optional[str] = Field(alias="avatar", default="")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPASettingsDefaults(BaseModel):
    amortization_type: Optional[str] = Field(alias="amortizationType", default=None)
    currency: Optional[str] = Field(alias="currency", default=None)
    flowExpirationMinutes: Optional[int] = Field(alias="flowExpirationMinutes", default=None)
    installments: Optional[int] = Field(alias="installments", default=None)
    repayEvery: Optional[int] = Field(alias="repayEvery", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Rate(BaseModel):
    period: Optional[int] = Field(alias="period", default=None)
    rate: Optional[str] = Field(alias="rate", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPASettingssInterestRates(BaseModel):
    period: Optional[int] = Field(alias="period", default=None)
    rate: Optional[Rate] = Field(alias="rate", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPASettingsPenalty(BaseModel):
    charge_code: Optional[str] = Field(alias="chargeCode", default=None)
    compute_every: Optional[int] = Field(alias="computeEvery", default=None)
    enabled: Optional[bool] = Field(alias="enabled", default=None)
    grace_period: Optional[int] = Field(alias="gracePeriod", default=None)
    rate: Optional[Rate] = Field(alias="rate", default=None)
    times_to_compute: Optional[int] = Field(alias="timesToCompute", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class DPASettingsDisbursement(BaseModel):
    disburse_to: Optional[str] = Field(alias="disburseTo", default="")


class DPASettingsAPIDTO(BaseModel):
    defaults: Optional[DPASettingsDefaults] = Field(alias="defaults", default=None)
    disbursement: Optional[DPASettingsDisbursement] = Field(alias="disbursement", default=None)
    interest_rates: List[DPASettingssInterestRates] = Field(alias="interestRates", default=None)
    invoice_over_limit: Optional[float] = Field(alias="invoiceOverLimit", default=None)
    on_approve_flow_reserve_all_assigned_amount: Optional[bool] = \
        Field(alias="onApproveFlowReserveAllAssignedAmount", default=None)
    penalties: List[DPASettingsPenalty] = Field(alias="penalties", default=[])
    reserve_on_start: Optional[bool] = Field(alias="reserveOnStart", default=None)
    tax_rate: Optional[float] = Field(alias="taxRate", default=None)
    timezone: Optional[str] = Field(alias="timezone", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class PartnerBase:

    def __init__(self, base_url):
        self.base_url = base_url


class PartnerAsync(PartnerBase):
    data: PartnerAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: PartnerAPIDTO):
        super().__init__(base_url)
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__})"


class PartnerSync(PartnerBase):
    data: PartnerAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: PartnerAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.partner_id})"


class PartnersAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            async_resource=PartnerAsync,
            retrieve_data_model=PartnerAPIDTO,
            create_data_model=CreatePartnerDTO,
            update_data_model=None,
            resource="partners",
            resource_version="v2"
        )

    @retry_on_401_async
    async def me(self) -> PartnerAsync:
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.get(
                "/v2/partners/me",
                # This is important to avoid infinite recursion
                headers=build_headers(self, partner_id=None),
                timeout=30
            )
            raise_for_status_improved(response)
            return PartnerAsync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=PartnerAPIDTO.parse_obj(response.json())
            )

    @retry_on_401_async
    async def update_dpa_settings(self, partner_id: str, settings: dict) -> DPASettingsAPIDTO:
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            settings = DPASettingsAPIDTO.parse_obj(settings)
            response = await client.patch(
                f"/v2/partners/{partner_id}/settings/dpa",
                json=settings.dict(by_alias=True, exclude_none=True),
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.parse_obj(response.json())


class PartnersSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(
            altscore_client=altscore_client,
            sync_resource=PartnerSync,
            retrieve_data_model=PartnerAPIDTO,
            create_data_model=CreatePartnerDTO,
            update_data_model=None,
            resource="partners",
            resource_version="v2"
        )

    @retry_on_401
    def me(self) -> PartnerSync:
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.get(
                "/v2/partners/me",
                # This is important to avoid infinite recursion
                headers=build_headers(self, partner_id="init"),
                timeout=30
            )
            raise_for_status_improved(response)
            return PartnerSync(
                base_url=self.altscore_client._cms_base_url,
                header_builder=self.build_headers,
                renew_token=self.renew_token,
                data=PartnerAPIDTO.parse_obj(response.json())
            )

    @retry_on_401
    def update_dpa_settings(self, partner_id: str, settings: dict) -> DPASettingsAPIDTO:
        settings = DPASettingsAPIDTO.parse_obj(settings)
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.patch(
                f"/v2/partners/{partner_id}/settings/dpa",
                json=settings.dict(by_alias=True, exclude_none=True),
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.parse_obj(response.json())
