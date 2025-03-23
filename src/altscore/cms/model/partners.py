import asyncio

from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from altscore.cms.model.calendars import CreateCalendarAPIDTO, DPACalendarAPIDTO
from altscore.cms.model.dpa_segmentation import DPASegmentationAPIDTO, CreateDPASegmentationDTO, \
    UpdateDPASegmentationDTO
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.cms.model.generics import GenericSyncModule, GenericAsyncModule
from altscore.cms.helpers import build_headers
from altscore.cms.model.dpa_products import DPAProductAPIDTO, CreateDPAProductAPIDTO, UpdateDPAProductAPIDTO
from altscore.borrower_central.utils import clean_dict, convert_to_dash_case


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
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreatePartnerDTO(BaseModel):
    name: str = Field(alias="name")
    short_name: str = Field(alias="shortName")
    email: str = Field(alias="email")
    tax_id: str = Field(alias="taxId")
    is_aggregator: Optional[bool] = Field(alias="isAggregator", default=False)
    avatar: Optional[str] = Field(alias="avatar", default="")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class DPASettingsDefaults(BaseModel):
    currency: Optional[str] = Field(alias="currency", default=None)
    flow_expiration_minutes: Optional[int] = Field(alias="flowExpirationMinutes", default=None)
    closing_balance_threshold: Optional[str] = Field(alias="closingBalanceThreshold", default=None)
    product_id: Optional[str] = Field(alias="productId", default=None)
    segmentation_id: Optional[str] = Field(alias="segmentationId", default=None)
    calendar_type: Optional[str] = Field(alias="calendarType", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class DPASettingsAPIDTO(BaseModel):
    partner_id: Optional[str] = Field(None, alias="partnerId")
    defaults: Optional[DPASettingsDefaults] = Field(alias="defaults", default=None)
    timezone: Optional[str] = Field(alias="timezone", default=None)
    on_approve_flow_reserve_all_assigned_amount: Optional[bool] = \
        Field(alias="onApproveFlowReserveAllAssignedAmount", default=None)
    invoice_over_limit: Optional[float] = Field(alias="invoiceOverLimit", default=None)
    reserve_on_start: Optional[bool] = Field(alias="reserveOnStart", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class PartnerBase:

    def __init__(self, base_url):
        self.base_url = base_url

    def _get_partner_dpa_products( self, partner_id:str, status: Optional[str]= None, sort_by: Optional[str] = None,
                per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
        ) -> (str, dict):
            query = {
                "status": status,
                "sort-by": sort_by,
                "per-page": per_page,
                "page": page,
                "sort-direction": sort_direction
            }
            return f"{self.base_url}/v2/partners/{partner_id}/products/dpa", clean_dict(query)

    def _get_partner_dpa_segmentations(self,
                                       partner_id:str,
                                       product_ids: Optional[List[str]]= None,
                                       status: Optional[str]= None,
                                       sort_by: Optional[str] = None,
                                        per_page: Optional[int] = None,
                                       page: Optional[int] = None,
                                       sort_direction: Optional[str] = None
        ) -> (str, dict):
        query = {
            "product-ids": ",".join(product_ids) if product_ids else None,
            "status": status,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v2/partners/{partner_id}/segmentations/dpa", clean_dict(query)

    def _get_partner_dpa_calendar (self, partner_id:str) -> (str, dict):
        return f"{self.base_url}/v2/partners/{partner_id}/calendar/dpa", {}

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

    @retry_on_401_async
    async def get_dpa_products(self, **kwargs) -> List[DPAProductAPIDTO]:
        url, query = self._get_partner_dpa_products(self.data.partner_id, **kwargs)
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query,
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPAProductAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401_async
    async def get_dpa_product(self, product_id: str) -> Optional[DPAProductAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPAProductAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401_async
    async def create_dpa_product(self, new_entity_data:dict) -> str:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v2/partners/{self.data.partner_id}/products/dpa",
                json=CreateDPAProductAPIDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["productId"]

    @retry_on_401_async
    async def delete_dpa_product(self, product_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def update_dpa_product(self, product_id: str, patch_data:dict) -> DPAProductAPIDTO:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                json=UpdateDPAProductAPIDTO.model_validate(patch_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPAProductAPIDTO.model_validate(response.json())

    @retry_on_401_async
    async def put_dpa_product_status(self, product_id: str, status: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.put(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}/status",
                headers=self._header_builder(),
                json={"status": status},
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_dpa_segmentations(self, **kwargs) -> List[DPASegmentationAPIDTO]:
        url, query = self._get_partner_dpa_segmentations(self.data.partner_id, **kwargs)
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query,
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPASegmentationAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401_async
    async def get_dpa_segmentation(self, segmentation_id: str) -> Optional[DPASegmentationAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPASegmentationAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401_async
    async def create_dpa_segmentation(self, new_entity_data:dict) -> str:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa",
                json=CreateDPASegmentationDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["segmentationId"]

    @retry_on_401_async
    async def update_dpa_segmentation(self, segmentation_id: str, patch_data:dict) -> DPASegmentationAPIDTO:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                json=UpdateDPASegmentationDTO.model_validate(patch_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASegmentationAPIDTO.model_validate(response.json())

    @retry_on_401_async
    async def put_dpa_segmentation_status(self, segmentation_id: str, status: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.put(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}/status",
                headers=self._header_builder(),
                json={"status": status},
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def delete_dpa_segmentation(self, segmentation_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_dpa_calendars(self) -> List[DPACalendarAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"{self.base_url}/v2/partners/{self.data.partner_id}/calendars/dpa",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPACalendarAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401_async
    async def get_dpa_calendar(self, calendar_id: str) -> Optional[DPACalendarAPIDTO]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa/{calendar_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPACalendarAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401_async
    async def create_dpa_calendar(self, new_entity_data:dict) -> str:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa",
                json=CreateCalendarAPIDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["calendarId"]


    @retry_on_401_async
    async def delete_dpa_calendar(self, calendar_id:str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa/{calendar_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)


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

    @retry_on_401
    def get_dpa_products(self, **kwargs) -> List[DPAProductAPIDTO]:
        url, query = self._get_partner_dpa_products(self.data.partner_id, **kwargs)
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query,
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPAProductAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401
    def get_dpa_product(self, product_id: str) -> Optional[DPAProductAPIDTO]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPAProductAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401
    def create_dpa_product(self, new_entity_data:dict):
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v2/partners/{self.data.partner_id}/products/dpa",
                json=CreateDPAProductAPIDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["productId"]

    @retry_on_401
    def delete_dpa_product(self, product_id: str) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.delete(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401
    def update_dpa_product(self, product_id: str, patch_data:dict) -> DPAProductAPIDTO:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.patch(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}",
                json=UpdateDPAProductAPIDTO.model_validate(patch_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPAProductAPIDTO.model_validate(response.json())

    @retry_on_401
    def put_dpa_product_status(self, product_id: str, status: str) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.put(
                f"/v2/partners/{self.data.partner_id}/products/dpa/{product_id}/status",
                headers=self._header_builder(),
                json={"status": status},
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401
    def get_dpa_segmentations(self, **kwargs) -> List[DPASegmentationAPIDTO]:
        url, query = self._get_partner_dpa_segmentations(self.data.partner_id, **kwargs)
        with httpx.Client(base_url=self.base_url) as client:
            response =  client.get(
                url,
                headers=self._header_builder(),
                params=query,
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPASegmentationAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401
    def get_dpa_segmentation(self, segmentation_id: str) -> Optional[DPASegmentationAPIDTO]:
         with httpx.Client(base_url=self.base_url) as client:
            response =  client.get(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPASegmentationAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401
    def create_dpa_segmentation(self, new_entity_data: dict) -> str:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa",
                json=CreateDPASegmentationDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["segmentationId"]

    @retry_on_401
    def update_dpa_segmentation(self, segmentation_id: str, patch_data: dict) -> DPASegmentationAPIDTO:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.patch(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                json=UpdateDPASegmentationDTO.model_validate(patch_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASegmentationAPIDTO.model_validate(response.json())

    @retry_on_401
    def put_dpa_segmentation_status(self, segmentation_id: str, status: str) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response =  client.put(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}/status",
                headers=self._header_builder(),
                json={"status": status},
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401
    def delete_dpa_segmentation(self, segmentation_id: str) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.delete(
                f"/v2/partners/{self.data.partner_id}/segmentations/dpa/{segmentation_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)

    @retry_on_401
    def get_dpa_calendars(self) -> List[DPACalendarAPIDTO]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"{self.base_url}/v2/partners/{self.data.partner_id}/calendars/dpa",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [DPACalendarAPIDTO.model_validate(e) for e in response.json()]

    @retry_on_401
    def get_dpa_calendar(self, calendar_id: str) -> Optional[DPACalendarAPIDTO]:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa/{calendar_id}",
                headers=self._header_builder(),
                timeout=30
            )
            if response.status_code == 404:
                return None
            elif response.status_code == 200:
                return DPACalendarAPIDTO.model_validate(response.json())
            raise_for_status_improved(response)

    @retry_on_401
    def create_dpa_calendar(self, new_entity_data: dict) -> str:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa",
                json=CreateCalendarAPIDTO.model_validate(new_entity_data).model_dump(by_alias=True, exclude_none=True),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()["calendarId"]

    @retry_on_401
    def delete_dpa_calendar(self, calendar_id: str) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.delete(
                f"/v2/partners/{self.data.partner_id}/calendars/dpa/{calendar_id}",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)


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
                data=PartnerAPIDTO.model_validate(response.json())
            )

    @retry_on_401_async
    async def get_dpa_settings(self, partner_id:str) -> DPASettingsAPIDTO:
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            response = await client.get(
                f"/v2/partners/{partner_id}/settings/dpa",
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.model_validate(response.json())

    @retry_on_401_async
    async def update_dpa_settings(self, partner_id: str, settings: dict) -> DPASettingsAPIDTO:
        async with httpx.AsyncClient(base_url=self.altscore_client._cms_base_url) as client:
            settings = DPASettingsAPIDTO.model_validate(settings)
            response = await client.patch(
                f"/v2/partners/{partner_id}/settings/dpa",
                json=settings.model_dump(by_alias=True, exclude_none=True),
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.model_validate(response.json())



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
                data=PartnerAPIDTO.model_validate(response.json())
            )

    @retry_on_401
    def get_dpa_settings(self, partner_id:str) -> DPASettingsAPIDTO:
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.get(
                f"/v2/partners/{partner_id}/settings/dpa",
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.model_validate(response.json())

    @retry_on_401
    def update_dpa_settings(self, partner_id: str, settings: dict) -> DPASettingsAPIDTO:
        settings = DPASettingsAPIDTO.model_validate(settings)
        with httpx.Client(base_url=self.altscore_client._cms_base_url) as client:
            response = client.patch(
                f"/v2/partners/{partner_id}/settings/dpa",
                json=settings.model_dump(by_alias=True, exclude_none=True),
                headers=build_headers(self),
                timeout=30
            )
            raise_for_status_improved(response)
            return DPASettingsAPIDTO.model_validate(response.json())


