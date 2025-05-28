import datetime as dt
from typing import Optional, Dict, List, Any
import httpx
from pydantic import BaseModel, Field

from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, GenericSyncModule, GenericAsyncModule

# ChangeSet DTOs
class ChangeSetDTO(BaseModel):
    id: str = Field(alias="id")
    batch_id: str = Field(alias="batchId")
    status: str = Field(alias="status")
    change_type: str = Field(alias="changeType")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class CreateChangeSetDTO(BaseModel):
    batch_id: str = Field(alias="batchId")
    change_type: str = Field(alias="changeType")
    status: Optional[str] = Field(alias="status", default="pending")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class UpdateChangeSetDTO(BaseModel):
    status: Optional[str] = Field(alias="status", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

# ChangeItem DTOs
class ChangeItemDTO(BaseModel):
    id: str = Field(alias="id")
    change_set_id: str = Field(alias="changeSetId")
    change_type: str = Field(alias="changeType")
    entity_id: str = Field(alias="entityId")
    suggested_values: Dict[str, Any] = Field(alias="suggestedValues")
    overriden_values: Dict[str, Any] = Field(alias="overridenValues", default={})
    context: Dict[str, Any] = Field(alias="context", default={})
    last_overriden_by: Optional[str] = Field(alias="lastOverridenBy", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class CreateChangeItemDTO(BaseModel):
    change_set_id: str = Field(alias="changeSetId")
    change_type: str = Field(alias="changeType")
    entity_id: str = Field(alias="entityId")
    suggested_values: Dict[str, Any] = Field(alias="suggestedValues")
    overriden_values: Optional[Dict[str, Any]] = Field(alias="overridenValues", default=None)
    context: Optional[Dict[str, Any]] = Field(alias="context", default=None)
    last_overriden_by: Optional[str] = Field(alias="lastOverridenBy", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class UpdateChangeItemDTO(BaseModel):
    overriden_values: Optional[Dict[str, Any]] = Field(alias="overridenValues", default=None)
    context: Optional[Dict[str, Any]] = Field(alias="context", default=None)
    last_overriden_by: Optional[str] = Field(alias="lastOverridenBy", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class OperationDTO(BaseModel):
    type: str = Field(alias="type")
    field: str = Field(alias="field")
    value: Optional[Any] = Field(alias="value", default=None)
    percentage: Optional[float] = Field(alias="percentage", default=None)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class RunOperationRequest(BaseModel):
    context_selector: Dict[str, Any] = Field(alias="contextSelector")
    operation: OperationDTO = Field(alias="operation")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class RunOperationResponse(BaseModel):
    affected_count: int = Field(alias="affectedCount")
    operation_type: str = Field(alias="operationType")
    field: str = Field(alias="field")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class ChangeSetSummaryByRiskRatingDTO(BaseModel):
    risk_rating: str = Field(alias="riskRating")
    count: int = Field(alias="count")
    credit_limit_total: float = Field(alias="creditLimitTotal")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


# Resource classes
class ChangeSetSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "change-sets", header_builder, renew_token, ChangeSetDTO.parse_obj(data))

class ChangeSetAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "change-sets", header_builder, renew_token, ChangeSetDTO.parse_obj(data))

class ChangeItemSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "change-items", header_builder, renew_token, ChangeItemDTO.parse_obj(data))

class ChangeItemAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "change-items", header_builder, renew_token, ChangeItemDTO.parse_obj(data))

# Module classes
class ChangeSetSyncModule(GenericSyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=ChangeSetSync,
                         retrieve_data_model=ChangeSetDTO,
                         create_data_model=CreateChangeSetDTO,
                         update_data_model=UpdateChangeSetDTO,
                         resource="change-sets")

    @retry_on_401
    def get_change_items(self, change_set_id: str, sort_by: Optional[str] = "_id", 
                        sort_direction: Optional[str] = "desc", page: Optional[int] = 1, 
                        per_page: Optional[int] = 10) -> Dict:
        """Get change items for a specific change set"""
        with httpx.Client(base_url=self.base_url) as client:
            params = {
                "sort-by": sort_by,
                "sort-direction": sort_direction,
                "page": page,
                "per-page": per_page
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            response = client.get(
                f"/{self.resource}/{change_set_id}/change-items",
                headers=self.header_builder(),
                params=params,
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def create_change_item(self, change_set_id: str, dto: CreateChangeItemDTO) -> Dict:
        """Create a new change item for a specific change set"""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/{self.resource}/{change_set_id}/change-items",
                headers=self.header_builder(),
                json=dto.dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def run_operation(self, change_set_id: str, dto: RunOperationRequest) -> RunOperationResponse:
        """Run an operation (set or scale) on change items matching context filters"""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"/{self.resource}/{change_set_id}/commands/run-operation",
                headers=self.header_builder(),
                json=dto.dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return RunOperationResponse.parse_obj(response.json())

    @retry_on_401
    def get_summary_by_risk_rating(self, change_set_id: str) -> List[ChangeSetSummaryByRiskRatingDTO]:
        """Get summary of preapproval change items grouped by risk rating"""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                f"/{self.resource}/{change_set_id}/summary-by-risk-rating",
                headers=self.header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [ChangeSetSummaryByRiskRatingDTO.parse_obj(item) for item in response.json()]


class ChangeSetAsyncModule(GenericAsyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=ChangeSetAsync,
                         retrieve_data_model=ChangeSetDTO,
                         create_data_model=CreateChangeSetDTO,
                         update_data_model=UpdateChangeSetDTO,
                         resource="change-sets")

    @retry_on_401_async
    async def get_change_items(self, change_set_id: str, sort_by: Optional[str] = "_id",
                              sort_direction: Optional[str] = "desc", page: Optional[int] = 1, 
                              per_page: Optional[int] = 10) -> Dict:
        """Get change items for a specific change set"""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            params = {
                "sort-by": sort_by,
                "sort-direction": sort_direction,
                "page": page,
                "per-page": per_page
            }
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await client.get(
                f"/{self.resource}/{change_set_id}/change-items",
                headers=self.header_builder(),
                params=params,
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def create_change_item(self, change_set_id: str, dto: CreateChangeItemDTO) -> Dict:
        """Create a new change item for a specific change set"""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/{self.resource}/{change_set_id}/change-items",
                headers=self.header_builder(),
                json=dto.dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def run_operation(self, change_set_id: str, dto: RunOperationRequest) -> RunOperationResponse:
        """Run an operation (set or scale) on change items matching context filters"""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"/{self.resource}/{change_set_id}/commands/run-operation",
                headers=self.header_builder(),
                json=dto.dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return RunOperationResponse.parse_obj(response.json())

    @retry_on_401_async
    async def get_summary_by_risk_rating(self, change_set_id: str) -> List[ChangeSetSummaryByRiskRatingDTO]:
        """Get summary of preapproval change items grouped by risk rating"""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                f"/{self.resource}/{change_set_id}/summary-by-risk-rating",
                headers=self.header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return [ChangeSetSummaryByRiskRatingDTO.parse_obj(item) for item in response.json()]


