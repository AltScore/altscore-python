from typing import Optional, List, Dict, Any
import httpx
from altscore.altdata.model.data_request import RequestResult
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from pydantic import BaseModel, Field


class PackageAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: Optional[str] = Field(alias="borrowerId")
    source_id: Optional[str] = Field(alias="sourceId", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)
    alias: Optional[str] = Field(alias="alias", default=None)
    label: Optional[str] = Field(alias="label", default=None)
    tags: List[str] = Field(alias="tags")
    forced_stale: Optional[bool] = Field(alias="forcedStale", default=False)
    created_at: str = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreatePackageDTO(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerId")
    source_id: Optional[str] = Field(alias="sourceId", default=None)
    workflow_id: Optional[str] = Field(alias="workflowId", default=None)
    alias: Optional[str] = Field(alias="alias", default=None)
    label: Optional[str] = Field(alias="label", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)
    tags: List[str] = Field(alias="tags", default=[])
    content: Any = Field(alias="content")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class PackageSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, data: Dict):
        super().__init__(base_url, "/stores/packages", header_builder, PackageAPIDTO.parse_obj(data))


class PackageAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, data: Dict):
        super().__init__(base_url, "/stores/packages", header_builder, PackageAPIDTO.parse_obj(data))


class PackagesSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=PackageSync,
                         retrieve_data_model=PackageAPIDTO,
                         create_data_model=CreatePackageDTO,
                         update_data_model=None,
                         resource="stores/packages")

    def force_stale(self, package_id: Optional[str] = None, borrower_id: Optional[str] = None,
                    workflow_id: Optional[str] = None, alias: Optional[str] = None):
        if package_id is None and borrower_id is None and workflow_id is None and alias is None:
            raise ValueError("At least one of package_id, borrower_id, workflow_id or alias must be provided")
        body = {
            "packageId": package_id,
            "borrowerId": borrower_id,
            "workflowId": workflow_id,
            "alias": alias,
            "forcedStale": True
        }
        body = {k: v for k, v in body.items() if v is not None}
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            client.put(
                "/stores/packages/stale",
                json=body,
                headers=self.build_headers()
            )

    def create_from_altdata_request_result(
            self, borrower_id: str, source_id: str, altdata_request_result: RequestResult,
            attachments: Optional[List[Dict[str, Any]]] = None,
    ):
        package = altdata_request_result.to_package(source_id)
        bc_source_id = "AD_{}_{}".format(source_id, package["version"])
        package_data = {
            "borrower_id": borrower_id,
            "source_id": bc_source_id,
            "content": package,
        }
        created_package_id = self.create(package_data)
        if attachments is not None:
            package_obj: PackageSync = self.retrieve(created_package_id)
            if package_obj is not None:
                for attachment in attachments:
                    package_obj.post_attachment(
                        attachment
                    )
        return created_package_id

    def create_all_from_altdata_request_result(
            self, borrower_id: str, altdata_request_result: RequestResult,
    ) -> Dict[str, str]:
        packages = {}
        for source_call_summary in altdata_request_result.call_summary:
            if source_call_summary.is_success:
                package_id = self.create_from_altdata_request_result(borrower_id=borrower_id,
                                                                     source_id=source_call_summary.source_id,
                                                                     altdata_request_result=altdata_request_result)
                packages[source_call_summary.source_id] = package_id
        return packages


class PackagesAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=PackageAsync,
                         retrieve_data_model=PackageAPIDTO,
                         create_data_model=CreatePackageDTO,
                         update_data_model=None,
                         resource="/stores/packages")

    async def create_from_altdata_request_result(
            self, borrower_id: str, source_id: str, altdata_request_result: RequestResult,
            attachments: Optional[List[Dict[str, Any]]] = None,
    ):
        package = altdata_request_result.to_package(source_id)
        bc_source_id = "AD_{}_{}".format(source_id, package["version"])
        package_data = {
            "borrower_id": borrower_id,
            "source_id": bc_source_id,
            "content": package,
        }
        created_package_id = await self.create(package_data)
        if attachments is not None:
            package_obj: PackageSync = await self.retrieve(created_package_id)
            if package_obj is not None:
                for attachment in attachments:
                    await package_obj.post_attachment(
                        attachment
                    )
        return created_package_id

    async def create_all_from_altdata_request_result(
            self, borrower_id: str, altdata_request_result: RequestResult,
    ) -> Dict[str, str]:
        packages = {}
        for source_call_summary in altdata_request_result.call_summary:
            if source_call_summary.is_success:
                package_id = await self.create_from_altdata_request_result(
                    borrower_id=borrower_id,
                    source_id=source_call_summary.source_id,
                    altdata_request_result=altdata_request_result)
                packages[source_call_summary.source_id] = package_id
        return packages
