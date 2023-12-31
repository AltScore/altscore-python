from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from altscore.borrower_central.helpers import build_headers
from altscore.borrower_central.model.identities import IdentitySync, IdentityAsync
from altscore.borrower_central.model.documents import DocumentSync, DocumentAsync, DocumentsAsyncModule, \
    DocumentsSyncModule
from altscore.borrower_central.model.addresses import AddressSync, AddressAsync
from altscore.borrower_central.model.points_of_contact import PointOfContactSync, PointOfContactAsync
from altscore.borrower_central.model.borrower_fields import BorrowerFieldSync, BorrowerFieldAsync
from altscore.borrower_central.model.authorizations import AuthorizationSync, AuthorizationAsync
from altscore.borrower_central.model.relationships import RelationshipSync, RelationshipAsync
from altscore.common.http_errors import raise_for_status_improved
from altscore.borrower_central.model.store_packages import PackageSync, PackageAsync
from altscore.borrower_central.model.executions import ExecutionSync, ExecutionAsync
from altscore.borrower_central.utils import clean_dict

import datetime as dt


class BorrowerAPIDTO(BaseModel):
    id: str = Field(alias="id")
    persona: str = Field(alias="persona")
    form_id: Optional[str] = Field(alias="formId", default=None)
    label: Optional[str] = Field(alias="label")
    tags: List[str] = Field(alias="tags", default=[])
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class CreateBorrowerDTO(BaseModel):
    persona: str = Field(alias="persona")
    label: Optional[str] = Field(alias="label")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class UpdateBorrowerDTO(BaseModel):
    label: Optional[str] = Field(alias="label", default=None)
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class BorrowerBase:
    resource = "borrowers"

    def __init__(self, base_url):
        self.base_url = base_url


    def _authorizations(
            self, borrower_id: str, sort_by: Optional[str] = None, key: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "key": key,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/authorizations", clean_dict(query)

    def _addresses(
            self, borrower_id: str, priority: Optional[int] = None, sort_by: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "priority": priority,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/addresses", clean_dict(query)

    def _identities(
            self, borrower_id: str, priority: Optional[int] = None, sort_by: Optional[str] = None,
            key: Optional[str] = None, per_page: Optional[int] = None, page: Optional[int] = None,
            sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "key": key,
            "priority": priority,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/identities", clean_dict(query)

    def _documents(
            self, borrower_id: str, key: Optional[str] = None, sort_by: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "key": key,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/documents", clean_dict(query)

    def _points_of_contact(
            self, borrower_id: str, contact_method: Optional[str], priority: Optional[int] = None,
            sort_by: Optional[str] = None, per_page: Optional[int] = None, page: Optional[int] = None,
            sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "priority": priority,
            "contact-method": contact_method,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/points-of-contact", clean_dict(query)

    def _relationships(
            self, borrower_id: str, priority: Optional[int] = None, sort_by: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None,
            is_legal_representative: Optional[bool] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "priority": priority,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction,
            "is-legal-representative": is_legal_representative
        }
        return f"{self.base_url}/v1/relationships", clean_dict(query)

    def _borrower_fields(
            self, borrower_id: str, key: Optional[str] = None, sort_by: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "key": key,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/borrower-fields", clean_dict(query)

    def _packages(
            self, borrower_id: str, source_id: Optional[str], sort_by: Optional[str] = None,
            per_page: Optional[int] = None, page: Optional[int] = None, sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "borrower-id": borrower_id,
            "source-id": source_id,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/stores/packages", clean_dict(query)

    def _executions(
            self, borrower_id: str, execution_id: Optional[str], workflow_id: Optional[str],
            sort_by: Optional[str] = None, per_page: Optional[int] = None, page: Optional[int] = None,
            sort_direction: Optional[str] = None
    ) -> (str, dict):
        query = {
            "billable-id": borrower_id,
            "workflow-id": workflow_id,
            "execution-id": execution_id,
            "sort-by": sort_by,
            "per-page": per_page,
            "page": page,
            "sort-direction": sort_direction
        }
        return f"{self.base_url}/v1/executions", clean_dict(query)


class BorrowersAsyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self):
        return build_headers(self)

    async def create(self, new_entity_data: dict):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                "/v1/borrowers",
                headers=self.build_headers(),
                json=CreateBorrowerDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["id"]

    async def patch(self, resource_id: str, patch_data: dict):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.patch(
                f"/v1/borrowers/{resource_id}",
                headers=self.build_headers(),
                json=UpdateBorrowerDTO.parse_obj(patch_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return await self.retrieve(response.json()["id"])

    async def delete(self, resource_id: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.delete(
                f"/v1/borrowers/{resource_id}",
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return None

    async def retrieve(self, resource_id: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                f"/v1/borrowers/{resource_id}",
                headers=self.build_headers(),
                timeout=120,
            )
            if response.status_code == 200:
                return BorrowerAsync(
                    base_url=self.altscore_client._borrower_central_base_url,
                    header_builder=self.build_headers,
                    data=BorrowerAPIDTO.parse_obj(response.json())
                )
            return None

    async def find_one_by_identity(self, identity_key: str, identity_value: str):
        """
        Exact match by identity
        """
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            identities_found_request = await client.get(
                f"/v1/identities",
                params={
                    "key": identity_key,
                    "value": identity_value,
                    "per-page": 1,
                    "page": 1
                },
                headers=self.build_headers(),
                timeout=120,
            )
            if identities_found_request.status_code == 200:
                identities_found_data = identities_found_request.json()
                if len(identities_found_data) == 0:
                    return None
                else:
                    if identities_found_data[0]["value"] == identity_value:
                        return await self.retrieve(identities_found_data[0]["borrowerId"])
            return None


class BorrowersSyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self):
        return build_headers(self)

    def create(self, new_entity_data: dict):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                "/v1/borrowers",
                headers=self.build_headers(),
                json=CreateBorrowerDTO.parse_obj(new_entity_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["id"]

    def patch(self, resource_id: str, patch_data: dict):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.patch(
                f"/v1/borrowers/{resource_id}",
                headers=self.build_headers(),
                json=UpdateBorrowerDTO.parse_obj(patch_data).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return self.retrieve(response.json()["id"])

    def delete(self, resource_id: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.delete(
                f"/v1/borrowers/{resource_id}",
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)
            return None

    def retrieve(self, borrower_id: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                f"/v1/borrowers/{borrower_id}",
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 200:
                return BorrowerSync(
                    base_url=self.altscore_client._borrower_central_base_url,
                    header_builder=self.build_headers,
                    data=BorrowerAPIDTO.parse_obj(response.json())
                )
            elif response.status_code in [403, 401]:
                raise Exception("Unauthorized, check your API key")
            return None

    def find_one_by_identity(self, identity_key: str, identity_value: str):
        """
        Exact match by identity
        """
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            identities_found_request = client.get(
                f"/v1/identities",
                params={
                    "key": identity_key,
                    "value": identity_value,
                    "per-page": 1,
                    "page": 1
                },
                headers=self.build_headers(),
                timeout=120,
            )
            if identities_found_request.status_code == 200:
                identities_found_data = identities_found_request.json()
                if len(identities_found_data) == 0:
                    return None
                else:
                    if identities_found_data[0]["value"] == identity_value:
                        return self.retrieve(identities_found_data[0]["borrowerId"])
            return None


class BorrowerAsync(BorrowerBase):
    data: BorrowerAPIDTO

    def __init__(self, base_url, header_builder, data: BorrowerAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.data = data

    async def get_documents(self, **kwargs) -> List[DocumentAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._documents(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [DocumentAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=document_data
            ) for document_data in data]

    async def get_identities(self, **kwargs) -> List[IdentityAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._identities(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [IdentityAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=identity_data
            ) for identity_data in data]

    async def get_addresses(self, **kwargs) -> List[AddressAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._addresses(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [AddressAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=address_data
            ) for address_data in data]

    async def get_points_of_contact(self, **kwargs) -> List[PointOfContactAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._points_of_contact(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [PointOfContactAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=point_of_contact_data
            ) for point_of_contact_data in data]

    async def get_borrower_fields(self, **kwargs) -> List[BorrowerFieldAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._borrower_fields(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [BorrowerFieldAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=borrower_field_data
            ) for borrower_field_data in data]

    async def get_authorizations(self, **kwargs) -> List[AuthorizationAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._authorizations(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [AuthorizationAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=authorization_data
            ) for authorization_data in data]

    async def get_relationships(self, **kwargs) -> List[RelationshipAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._relationships(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [RelationshipAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=relationship_data
            ) for relationship_data in data]

    async def get_executions(self, **kwargs) -> List[ExecutionAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._executions(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [ExecutionAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=execution_data
            ) for execution_data in data]

    async def get_packages(self, **kwargs) -> List[PackageAsync]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            url, query = self._packages(self.data.id, **kwargs)
            response = await client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [PackageAsync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=package_data
            ) for package_data in data]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"


class BorrowerSync(BorrowerBase):
    data: BorrowerAPIDTO

    def __init__(self, base_url, header_builder, data: BorrowerAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.data = data

    def get_documents(self, **kwargs) -> List[DocumentSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._documents(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [DocumentSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=document_data
            ) for document_data in data]

    def get_identities(self, **kwargs) -> List[IdentitySync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._identities(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [IdentitySync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=identity_data
            ) for identity_data in data]

    def get_addresses(self, **kwargs) -> List[AddressSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._addresses(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [AddressSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=address_data
            ) for address_data in data]

    def get_points_of_contact(self, **kwargs) -> List[PointOfContactSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._points_of_contact(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [PointOfContactSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=point_of_contact_data
            ) for point_of_contact_data in data]

    def get_borrower_fields(self, **kwargs) -> List[BorrowerFieldSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._borrower_fields(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [BorrowerFieldSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=borrower_field_data
            ) for borrower_field_data in data]

    def get_authorizations(self, **kwargs) -> List[AuthorizationSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._authorizations(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [AuthorizationSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=authorization_data
            ) for authorization_data in data]

    def get_relationships(self, **kwargs) -> List[RelationshipSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._relationships(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [RelationshipSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=relationship_data
            ) for relationship_data in data]

    def get_executions(self, **kwargs) -> List[ExecutionSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._executions(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [ExecutionSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=execution_data
            ) for execution_data in data]

    def get_packages(self, **kwargs) -> List[PackageSync]:
        with httpx.Client(base_url=self.base_url) as client:
            url, query = self._packages(self.data.id, **kwargs)
            response = client.get(
                url,
                headers=self._header_builder(),
                params=query
            )
            data = response.json()
            return [PackageSync(
                base_url=self.base_url,
                header_builder=self._header_builder,
                data=package_data
            ) for package_data in data]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.id})"