import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from pydantic import BaseModel, Field, root_validator
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from altscore.borrower_central.utils import build_test_params
import datetime as dt


class Money(BaseModel):
    amount: str = Field(alias="amount")
    currency: str = Field(alias="currency")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class HistoricValue(BaseModel):
    reference_id: str = Field(alias="referenceId")  # this is the id an identifier for the source of the value
    value: Any = Field(alias="value")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class BorrowerFieldAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")
    label: Optional[str] = Field(alias="label", default=None)
    value: Any = Field(alias="value")
    data_type: str = Field(alias="dataType")
    history: List[HistoricValue] = Field(alias="history")
    tags: List[str] = Field(alias="tags", default=[])
    is_test: Optional[bool] = Field(alias="isTest", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    @root_validator(pre=False)
    def parse_history_values(cls, values):
        """Parse history values based on the field's data_type"""
        data_type = values.get("data_type")
        history = values.get("history", [])
        
        # Parse current value based on data_type
        current_value = values.get("value")
        if data_type == "money" and isinstance(current_value, dict):
            values["value"] = Money.parse_obj(current_value)
        
        # Parse history values based on data_type
        if history:
            for hist_item in history:
                if data_type == "money" and isinstance(hist_item.value, dict):
                    hist_item.value = Money.parse_obj(hist_item.value)
        
        return values


class CreateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    key: str = Field(alias="key")
    value: Any = Field(alias="value")
    data_type: Optional[str] = Field(alias="dataType", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    updated_at: Optional[dt.datetime] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    def dict(self, *args, **kwargs):
        base_dict = super().dict(*args, **kwargs)
        date_key = 'updatedAt' if kwargs.get("by_alias") else 'updated_at'
        base_dict[date_key] = self.updated_at.isoformat() if self.updated_at else None
        return base_dict


class UpdateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    value: Optional[Any] = Field(alias="value")
    data_type: Optional[str] = Field(alias="dataType", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    updated_at: Optional[dt.datetime] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    def dict(self, *args, **kwargs):
        base_dict = super().dict(*args, **kwargs)
        date_key = 'updatedAt' if kwargs.get("by_alias") else 'updated_at'
        base_dict[date_key] = self.updated_at.isoformat() if self.updated_at else None
        return base_dict


class BorrowerFieldSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=BorrowerFieldSync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")

    @retry_on_401
    def find_by_key(self, key: str, borrower_id: str,
                    include_tests: bool = True, test_only: bool = False):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            params = build_test_params({
                "key": key,
                "borrower-id": borrower_id,
                "per-page": 1,
                "page": 1
            }, include_tests=include_tests, test_only=test_only)
            fields_found_req = client.get(
                f"/v1/borrower-fields",
                params=params,
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(fields_found_req)
            fields_found_data = fields_found_req.json()
            if len(fields_found_data) == 0:
                return None
            else:
                return self.retrieve(fields_found_data[0]["id"])

    def count_distinct_values(self, key: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            unique_values_req = client.get(
                f"/v1/borrower-fields/queries/count-distinct-values",
                params={
                    "key": key
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(unique_values_req)
            return unique_values_req.json()

    def bulk_update_field_values(self, key: str, current_value: str, target_value: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                f"/v1/borrower-fields/commands/bulk-update-values",
                json={
                    "key": key,
                    "currentValue": current_value,
                    "targetValue": target_value
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return

    @retry_on_401
    def bulk_update_by_borrower_ids(self, borrower_ids: List[str], key: str, new_value: Any, reference_id: Optional[str] = None):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            payload = {
                "borrowerIds": borrower_ids,
                "key": key,
                "newValue": new_value
            }
            if reference_id is not None:
                payload["referenceId"] = reference_id
                
            response = client.post(
                f"/v1/borrower-fields/commands/bulk-update-by-borrower-ids",
                json=payload,
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return

    @retry_on_401
    def get_by_borrower_id(self, borrower_id: str, page: int = 1, per_page: int = 100,
                           include_tests: bool = True, test_only: bool = False):
        """
        Get all borrower fields for a specific borrower

        Args:
            borrower_id: The ID of the borrower
            page: Page number for pagination
            per_page: Number of results per page
            include_tests: Include test entities in results (default True)
            test_only: Return only test entities (default False)

        Returns:
            List[BorrowerFieldSync]: List of borrower fields for the borrower
        """
        query_kwargs = {
            "borrower_id": borrower_id,
            "page": page,
            "per_page": per_page,
        }
        if test_only:
            query_kwargs["test_only"] = True
        elif include_tests:
            query_kwargs["include_tests"] = True
        return self.query(**query_kwargs)

class BorrowerFieldsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=BorrowerFieldAsync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")

    @retry_on_401_async
    async def find_by_key(self, key: str, borrower_id: str,
                          include_tests: bool = True, test_only: bool = False):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            params = build_test_params({
                "key": key,
                "borrower-id": borrower_id,
                "per-page": 1,
                "page": 1
            }, include_tests=include_tests, test_only=test_only)
            fields_found_req = await client.get(
                f"/v1/borrower-fields",
                params=params,
                headers=self.build_headers(),
                timeout=120,
            )
            raise_for_status_improved(fields_found_req)
            fields_found_data = fields_found_req.json()
            if len(fields_found_data) == 0:
                return None
            else:
                return await self.retrieve(fields_found_data[0]["id"])


    async def count_distinct_values(self, key: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            unique_values_req = await client.get(
                f"/v1/borrower-fields/queries/count-distinct-values",
                params={
                    "key": key
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(unique_values_req)
            return unique_values_req.json()


    async def bulk_update_field_values(self, key: str, current_value: str, target_value: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                f"/v1/borrower-fields/commands/bulk-update-values",
                json={
                    "key": key,
                    "currentValue": current_value,
                    "targetValue": target_value
                },
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def bulk_update_by_borrower_ids(self, borrower_ids: List[str], key: str, new_value: Any, reference_id: Optional[str] = None):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            payload = {
                "borrowerIds": borrower_ids,
                "key": key,
                "newValue": new_value
            }
            if reference_id is not None:
                payload["referenceId"] = reference_id
                
            response = await client.post(
                f"/v1/borrower-fields/commands/bulk-update-by-borrower-ids",
                json=payload,
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_by_borrower_id(self, borrower_id: str, page: int = 1, per_page: int = 100,
                                 include_tests: bool = True, test_only: bool = False):
        """
        Get all borrower fields for a specific borrower

        Args:
            borrower_id: The ID of the borrower
            page: Page number for pagination
            per_page: Number of results per page
            include_tests: Include test entities in results (default True)
            test_only: Return only test entities (default False)

        Returns:
            List[BorrowerFieldAsync]: List of borrower fields for the borrower
        """
        query_kwargs = {
            "borrower_id": borrower_id,
            "page": page,
            "per_page": per_page,
        }
        if test_only:
            query_kwargs["test_only"] = True
        elif include_tests:
            query_kwargs["include_tests"] = True
        return await self.query(**query_kwargs)