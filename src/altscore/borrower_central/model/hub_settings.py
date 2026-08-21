import httpx
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers


class ExecutionLimitPeriodType(str, Enum):
    LIFETIME = "lifetime"
    MONTHLY = "monthly"


class ExecutionLimitConfig(BaseModel):
    max_executions: int = Field(alias="maxExecutions", ge=1)
    period_type: ExecutionLimitPeriodType = Field(alias="periodType")
    reset_day_of_month: Optional[int] = Field(alias="resetDayOfMonth", default=1, ge=1, le=28)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ExecutionUsage(BaseModel):
    configured: bool = Field(alias="configured")
    current_count: Optional[int] = Field(alias="currentCount", default=None)
    max_executions: Optional[int] = Field(alias="maxExecutions", default=None)
    remaining: Optional[int] = Field(alias="remaining", default=None)
    period_type: Optional[str] = Field(alias="periodType", default=None)
    reset_day_of_month: Optional[int] = Field(alias="resetDayOfMonth", default=None)
    period_start: Optional[str] = Field(alias="periodStart", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class HubSettingsSyncModule:
    """Tenant-level Hub settings. The execution-limit endpoints require the
    caller's token to carry the `workflows_admin` ROLE -- a role check, not an
    entitlement, so feature bundles do not grant it."""

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401
    def retrieve(self) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}/v1/application/hub-settings"
        with httpx.Client() as client:
            response = client.get(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def set_execution_limit(
        self,
        max_executions: int,
        period_type: ExecutionLimitPeriodType = ExecutionLimitPeriodType.LIFETIME,
        reset_day_of_month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Upsert the tenant's execution limit. No settings document needs to
        exist beforehand. `reset_day_of_month` only applies to MONTHLY."""
        config = ExecutionLimitConfig.parse_obj({
            "maxExecutions": max_executions,
            "periodType": period_type,
            "resetDayOfMonth": reset_day_of_month if reset_day_of_month is not None else 1
        })
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-limit-config"
        with httpx.Client() as client:
            response = client.put(
                url,
                headers=self.build_headers(),
                json=config.dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def delete_execution_limit(self) -> None:
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-limit-config"
        with httpx.Client() as client:
            response = client.delete(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)

    @retry_on_401
    def get_execution_usage(self) -> ExecutionUsage:
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-usage"
        with httpx.Client() as client:
            response = client.get(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)
            return ExecutionUsage.parse_obj(response.json())


class HubSettingsAsyncModule:
    """Async counterpart of HubSettingsSyncModule."""

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401_async
    async def retrieve(self) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}/v1/application/hub-settings"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def set_execution_limit(
        self,
        max_executions: int,
        period_type: ExecutionLimitPeriodType = ExecutionLimitPeriodType.LIFETIME,
        reset_day_of_month: Optional[int] = None
    ) -> Dict[str, Any]:
        config = ExecutionLimitConfig.parse_obj({
            "maxExecutions": max_executions,
            "periodType": period_type,
            "resetDayOfMonth": reset_day_of_month if reset_day_of_month is not None else 1
        })
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-limit-config"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                headers=self.build_headers(),
                json=config.dict(by_alias=True),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def delete_execution_limit(self) -> None:
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-limit-config"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)

    @retry_on_401_async
    async def get_execution_usage(self) -> ExecutionUsage:
        url = f"{self.altscore_client._borrower_central_base_url}" \
              f"/v1/application/hub-settings/execution-usage"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.build_headers(), timeout=30)
            raise_for_status_improved(response)
            return ExecutionUsage.parse_obj(response.json())
