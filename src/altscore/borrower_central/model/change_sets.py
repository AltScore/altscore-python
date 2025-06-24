# import datetime as dt
from typing import Optional, Dict, List, Any, Union, Literal
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
  locked_fields: Optional[Dict[str, bool]] = Field(alias="lockedFields", default=None)

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
  locked_fields: Optional[Dict[str, bool]] = Field(alias="lockedFields", default=None)

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
  overridden_values: Dict[str, Any] = Field(alias="overriddenValues", default={})
  context: Dict[str, Any] = Field(alias="context", default={})
  last_overridden_by: Optional[str] = Field(alias="lastOverriddenBy", default=None)
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
  overridden_values: Optional[Dict[str, Any]] = Field(alias="overriddenValues", default=None)
  context: Optional[Dict[str, Any]] = Field(alias="context", default=None)
  last_overridden_by: Optional[str] = Field(alias="lastOverriddenBy", default=None)

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class UpdateChangeItemDTO(BaseModel):
  overridden_values: Optional[Dict[str, Any]] = Field(alias="overriddenValues", default=None)
  context: Optional[Dict[str, Any]] = Field(alias="context", default=None)
  last_overridden_by: Optional[str] = Field(alias="lastOverriddenBy", default=None)
  skip_locking: Optional[bool] = Field(alias="skipLocking", default=False)

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

# Scope DTOs
class ContextScopeDTO(BaseModel):
  context: Dict[str, Any] = Field(alias="context")

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class EntityIdsScopeDTO(BaseModel):
  entity_ids: List[str] = Field(alias="entityIds")

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class AllChangeItemsScopeDTO(BaseModel):
  all_change_items: Literal[True] = Field(alias="allChangeItems")

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

ScopeDTO = Union[ContextScopeDTO, EntityIdsScopeDTO, AllChangeItemsScopeDTO]

class OperationDTO(BaseModel):
  type: Literal["set", "scale_by_percentage", "reset"] = Field(alias="type")
  scope: ScopeDTO = Field(alias="scope")
  field: Optional[str] = Field(alias="field", default=None)
  value: Optional[Union[str, int, float, bool]] = Field(alias="value", default=None)
  percentage: Optional[float] = Field(alias="percentage", default=None)

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class RunOperationRequest(BaseModel):
  operation: OperationDTO = Field(alias="operation")
  last_overridden_by: Optional[str] = Field(alias="lastOverriddenBy", default=None)

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class RunOperationResponse(BaseModel):
  affected_count: int = Field(alias="affectedCount")
  operation_type: str = Field(alias="operationType")
  field: Optional[str] = Field(alias="field", default=None)

  class Config:
      populate_by_name = True
      allow_population_by_field_name = True
      allow_population_by_alias = True

class ChangeSetSummaryByRiskRatingDTO(BaseModel):
  risk_rating: str = Field(alias="riskRating")
  total_count: int = Field(alias="totalCount")
  total_credit_line_limit: float = Field(alias="totalCreditLineLimit")
  preapproved_count: int = Field(alias="preapprovedCount")
  preapproved_credit_line_limit: float = Field(alias="preapprovedCreditLineLimit")

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
  def run_operation(self, change_set_id: str, dto: RunOperationRequest) -> RunOperationResponse:
      """Run an operation (set, scale, or reset) on change items using scope-based targeting"""
      with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
          response = client.post(
              f"/v1/{self.resource}/{change_set_id}/commands/run-operation",
              headers=self.build_headers(),
              json=dto.dict(),
              timeout=120
          )
          raise_for_status_improved(response)
          return RunOperationResponse.parse_obj(response.json())

  @retry_on_401
  def get_summary_by_risk_rating(self, change_set_id: str) -> List[ChangeSetSummaryByRiskRatingDTO]:
      """Get summary of preapproval change items grouped by risk rating"""
      with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
          response = client.get(
              f"/v1/{self.resource}/{change_set_id}/summary-by-risk-rating",
              headers=self.build_headers(),
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
  async def run_operation(self, change_set_id: str, dto: RunOperationRequest) -> RunOperationResponse:
      """Run an operation (set, scale, or reset) on change items using scope-based targeting"""
      async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
          response = await client.post(
              f"/v1/{self.resource}/{change_set_id}/commands/run-operation",
              headers=self.build_headers(),
              json=dto.dict(),
              timeout=120
          )
          raise_for_status_improved(response)
          return RunOperationResponse.parse_obj(response.json())

  @retry_on_401_async
  async def get_summary_by_risk_rating(self, change_set_id: str) -> List[ChangeSetSummaryByRiskRatingDTO]:
      """Get summary of preapproval change items grouped by risk rating"""
      async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
          response = await client.get(
              f"/v1/{self.resource}/{change_set_id}/summary-by-risk-rating",
              headers=self.build_headers(),
              timeout=30
          )
          raise_for_status_improved(response)
          return [ChangeSetSummaryByRiskRatingDTO.parse_obj(item) for item in response.json()]

class ChangeItemsSyncModule(GenericSyncModule):
  def __init__(self, altscore_client):
      super().__init__(altscore_client,
                       sync_resource=ChangeItemSync,
                       retrieve_data_model=ChangeItemDTO,
                       create_data_model=CreateChangeItemDTO,
                       update_data_model=UpdateChangeItemDTO,
                       resource="change-items")

class ChangeItemsAsyncModule(GenericAsyncModule):
  def __init__(self, altscore_client):
      super().__init__(altscore_client,
                       sync_resource=ChangeItemAsync,
                       retrieve_data_model=ChangeItemDTO,
                       create_data_model=CreateChangeItemDTO,
                       update_data_model=UpdateChangeItemDTO,
                       resource="change-items")
