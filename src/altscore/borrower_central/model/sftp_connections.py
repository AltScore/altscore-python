from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel, Field

from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers


class SFTPConnectionDTO(BaseModel):
    id: str = Field(alias="id")
    host: str = Field(alias="host")
    label: str = Field(alias="label")
    tenant: str = Field(alias="tenant")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class NewSFTPConnectionDTO(BaseModel):
    host: str = Field(alias="host")
    port: Optional[int] = Field(alias="port", default=22)
    username: str = Field(alias="username")
    password: str = Field(alias="password")
    label: str = Field(alias="label")
    base_path: Optional[str] = Field(alias="basePath", default="/")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPFileDTO(BaseModel):
    name: str = Field(alias="name")
    path: str = Field(alias="path")
    size: Optional[int] = Field(alias="size", default=None)
    isDirectory: bool = Field(alias="isDirectory", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPUploadResultDTO(BaseModel):
    uploaded_path: str = Field(alias="uploadedPath")
    file_size: int = Field(alias="fileSize")
    attachment_id: str = Field(alias="attachmentId")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPConnectionBase:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _get_connection_url(self, connection_id: str) -> str:
        return f"{self.base_url}/v1/sftp-connections/{connection_id}"

    def _list_files_url(self, connection_id: str) -> str:
        return f"{self.base_url}/v1/sftp-connections/{connection_id}/list"

    def _download_file_url(self, connection_id: str) -> str:
        return f"{self.base_url}/v1/sftp-connections/{connection_id}/download"

    def _upload_file_url(self, connection_id: str) -> str:
        return f"{self.base_url}/v1/sftp-connections/{connection_id}/upload"


class SFTPConnectionAsyncModule:
    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401_async
    async def create(self, new_connection: Dict[str, Any]) -> str:
        """Create a new SFTP connection and return its ID."""
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                "/v1/sftp-connections",
                headers=self.build_headers(),
                json=NewSFTPConnectionDTO.parse_obj(new_connection).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["id"]

    @retry_on_401_async
    async def retrieve(self, connection_id: str):
        """Retrieve an SFTP connection by ID."""
        base_url = self.altscore_client._borrower_central_base_url
        async with httpx.AsyncClient(base_url=base_url) as client:
            response = await client.get(
                f"/v1/sftp-connections/{connection_id}",
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 200:
                return SFTPConnectionAsync(
                    base_url=base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    connection_data=SFTPConnectionDTO.parse_obj(response.json())
                )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)

    @retry_on_401_async
    async def delete(self, connection_id: str):
        """Delete an SFTP connection."""
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.delete(
                f"/v1/sftp-connections/{connection_id}",
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)

    @retry_on_401_async
    async def query(self, tenant: Optional[str] = None) -> List[SFTPConnectionDTO]:
        """List all SFTP connections, optionally filtered by tenant."""
        params = {}
        if tenant:
            params["tenant"] = tenant

        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.get(
                "/v1/sftp-connections",
                headers=self.build_headers(),
                params=params,
                timeout=120
            )
            raise_for_status_improved(response)
            return [
                SFTPConnectionDTO.parse_obj(data)
                for data in response.json()
            ]

    @retry_on_401_async
    async def list_files(self, path: str = "/") -> List[SFTPFileDTO]:
        """List files and directories at the specified path."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._list_files_url(self.data.id),
                headers=self._header_builder(),
                params={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return [
                SFTPFileDTO.parse_obj(data)
                for data in response.json()
            ]

    @retry_on_401_async
    async def download_file(self, remote_path: str) -> str:
        """Download a file from SFTP and return the package ID."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._download_file_url(self.data.id),
                headers=self._header_builder(),
                json={"path": remote_path},
                timeout=300  # Downloads may take longer
            )
            raise_for_status_improved(response)
            return response.json()["package_id"]

    @retry_on_401_async
    async def upload_file(self, attachment_id: str, remote_path: str,
                          filename: Optional[str] = None) -> SFTPUploadResultDTO:
        """Upload a file from an attachment to SFTP."""
        payload = {
            "attachmentId": attachment_id,
            "remotePath": remote_path,
        }
        if filename:
            payload["filename"] = filename

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._upload_file_url(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300  # Uploads may take longer
            )
            raise_for_status_improved(response)
            return SFTPUploadResultDTO.parse_obj(response.json())

    @retry_on_401_async
    async def test_connection(self) -> Dict[str, Any]:
        """Test the SFTP connection."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                f"{self.base_url}/v1/sftp-connections/{self.data.id}/test",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def update(self, updates: Dict[str, Any]) -> SFTPConnectionDTO:
        """Update the SFTP connection."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(
                self._get_connection_url(self.data.id),
                headers=self._header_builder(),
                json=updates,
                timeout=120
            )
            raise_for_status_improved(response)
            updated_data = SFTPConnectionDTO.parse_obj(response.json())
            self.data = updated_data
            return updated_data


class SFTPConnectionSyncModule:
    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401
    def create(self, new_connection: Dict[str, Any]) -> str:
        """Create a new SFTP connection and return its ID."""
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                "/v1/sftp-connections",
                headers=self.build_headers(),
                json=NewSFTPConnectionDTO.parse_obj(new_connection).dict(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            return response.json()["id"]

    @retry_on_401
    def retrieve(self, connection_id: str):
        """Retrieve an SFTP connection by ID."""
        base_url = self.altscore_client._borrower_central_base_url
        with httpx.Client(base_url=base_url) as client:
            response = client.get(
                f"/v1/sftp-connections/{connection_id}",
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 200:
                return SFTPConnectionSync(
                    base_url=base_url,
                    header_builder=self.build_headers,
                    renew_token=self.renew_token,
                    connection_data=SFTPConnectionDTO.parse_obj(response.json())
                )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)

    @retry_on_401
    def delete(self, connection_id: str):
        """Delete an SFTP connection."""
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.delete(
                f"/v1/sftp-connections/{connection_id}",
                headers=self.build_headers(),
                timeout=120
            )
            raise_for_status_improved(response)

    @retry_on_401
    def list_all(self, tenant: Optional[str] = None) -> List[SFTPConnectionDTO]:
        """List all SFTP connections, optionally filtered by tenant."""
        params = {}
        if tenant:
            params["tenant"] = tenant

        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.get(
                "/v1/sftp-connections",
                headers=self.build_headers(),
                params=params,
                timeout=120
            )
            raise_for_status_improved(response)
            return [
                SFTPConnectionDTO.parse_obj(data)
                for data in response.json()
            ]


class SFTPConnectionAsync(SFTPConnectionBase):
    data: SFTPConnectionDTO

    def __init__(self, base_url, header_builder, renew_token, connection_data: SFTPConnectionDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = connection_data


class SFTPConnectionSync(SFTPConnectionBase):
    data: SFTPConnectionDTO

    def __init__(self, base_url, header_builder, renew_token, connection_data: SFTPConnectionDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = connection_data

    @retry_on_401
    def list_files(self, path: str = "/") -> List[SFTPFileDTO]:
        """List files and directories at the specified path."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._list_files_url(self.data.id),
                headers=self._header_builder(),
                params={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return [
                SFTPFileDTO.parse_obj(data)
                for data in response.json()
            ]

    @retry_on_401
    def download_file(self, remote_path: str) -> str:
        """Download a file from SFTP and return the package ID."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._download_file_url(self.data.id),
                headers=self._header_builder(),
                json={"path": remote_path},
                timeout=300  # Downloads may take longer
            )
            raise_for_status_improved(response)
            return response.json()["package_id"]

    @retry_on_401
    def upload_file(self, attachment_id: str, remote_path: str,
                    filename: Optional[str] = None) -> SFTPUploadResultDTO:
        """Upload a file from an attachment to SFTP."""
        payload = {
            "attachmentId": attachment_id,
            "remotePath": remote_path,
        }
        if filename:
            payload["filename"] = filename

        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._upload_file_url(self.data.id),
                headers=self._header_builder(),
                json=payload,
                timeout=300  # Uploads may take longer
            )
            raise_for_status_improved(response)
            return SFTPUploadResultDTO.parse_obj(response.json())

    @retry_on_401
    def test_connection(self) -> Dict[str, Any]:
        """Test the SFTP connection."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                f"{self.base_url}/v1/sftp-connections/{self.data.id}/test",
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def update(self, updates: Dict[str, Any]) -> SFTPConnectionDTO:
        """Update the SFTP connection."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.patch(
                self._get_connection_url(self.data.id),
                headers=self._header_builder(),
                json=updates,
                timeout=120
            )
            raise_for_status_improved(response)
            updated_data = SFTPConnectionDTO.parse_obj(response.json())
            self.data = updated_data
            return updated_data
