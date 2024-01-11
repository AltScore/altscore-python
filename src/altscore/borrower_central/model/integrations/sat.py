import datetime as dt
import httpx
from pydantic import BaseModel, Field
from altscore.common.http_errors import raise_for_status_improved
from altscore.borrower_central.helpers import build_headers


class ExtractionCoverageInfo(BaseModel):
    rfc: str
    date_from: str = Field(alias="dateFrom")
    date_to: str = Field(alias="dateTo")
    has_coverage: bool = Field(alias="hasCoverage")
    has_running_extractions: bool = Field(alias="hasRunningExtractions")

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SatIntegrationAsyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client
        self.base_url = self.altscore_client._borrower_central_base_url

    def build_headers(self):
        return build_headers(self)

    async def check_extractions(
            self, rfc: str, date_to_analyze: dt.datetime, days_of_tolerance: int) -> ExtractionCoverageInfo:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/integrations/sat/extractions/check",
                json={
                    "rfc": rfc,
                    "dateToAnalyze": date_to_analyze.isoformat(),
                    "daysOfTolerance": days_of_tolerance
                },
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return ExtractionCoverageInfo.parse_obj(response.json())

    async def start_extractions(
            self, rfc: str, date_to_analyze: dt.datetime) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/integrations/sat/extractions/start",
                json={
                    "rfc": rfc,
                    "dateToAnalyze": date_to_analyze.isoformat()
                },
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return None


class SatIntegrationSyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client
        self.base_url = self.altscore_client._borrower_central_base_url

    def build_headers(self):
        return build_headers(self)

    def check_extractions(
            self, rfc: str, date_to_analyze: dt.datetime, days_of_tolerance: int) -> ExtractionCoverageInfo:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                "/integrations/sat/extractions/check",
                json={
                    "rfc": rfc,
                    "dateToAnalyze": date_to_analyze.isoformat(),
                    "daysOfTolerance": days_of_tolerance
                },
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return ExtractionCoverageInfo.parse_obj(response.json())

    def start_extractions(
            self, rfc: str, date_to_analyze: dt.datetime) -> None:
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                "/integrations/sat/extractions/start",
                json={
                    "rfc": rfc,
                    "dateToAnalyze": date_to_analyze.isoformat()
                },
                headers=self.build_headers()
            )
            raise_for_status_improved(response)
            return None
