from typing import List, Optional, Dict, Any

import httpx
from pydantic import BaseModel, Field

from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, GenericSyncModule, \
    GenericAsyncModule


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
    port: Optional[int] = Field(alias="port", default=22, ge=1, le=65535)
    username: str = Field(alias="username", min_length=1)
    password: str = Field(alias="password", min_length=8)
    label: str = Field(alias="label", min_length=1)
    base_path: Optional[str] = Field(alias="basePath", default="/", min_length=1, regex=r'^/.*')

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPFileDTO(BaseModel):
    name: str = Field(alias="name")
    path: str = Field(alias="path")
    size: Optional[int] = Field(alias="size", default=None)
    is_directory: bool = Field(alias="isDirectory", default=False)

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


class SFTPConnectionSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=SFTPConnectionSync,
                         retrieve_data_model=SFTPConnectionDTO,
                         create_data_model=NewSFTPConnectionDTO,
                         update_data_model=NewSFTPConnectionDTO,
                         resource="sftp-connections")


class SFTPConnectionAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=SFTPConnectionAsync,
                         retrieve_data_model=SFTPConnectionDTO,
                         create_data_model=NewSFTPConnectionDTO,
                         update_data_model=NewSFTPConnectionDTO,
                         resource="sftp-connections")


class SFTPConnectionSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: SFTPConnectionDTO):
        super().__init__(base_url, "sftp-connections", header_builder, renew_token, data)
    
    def _url(self, action: str) -> str:
        return f"/v1/{self.resource}/{self.data.id}/{action}"

    @retry_on_401
    def list_files(self, path: str = "/") -> List[SFTPFileDTO]:
        """List files and directories at the specified path."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.get(
                self._url("list"),
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
                self._url("download"),
                headers=self._header_builder(),
                json={"path": remote_path},
                timeout=300  # Downloads may take longer
            )
            raise_for_status_improved(response)
            return response.json()["packageId"]

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
                self._url("upload"),
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
                self._url("test"),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()


class SFTPConnectionAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: SFTPConnectionDTO):
        super().__init__(base_url, "sftp-connections", header_builder, renew_token, data)
    
    def _url(self, action: str) -> str:
        return f"/v1/{self.resource}/{self.data.id}/{action}"

    @retry_on_401_async
    async def list_files(self, path: str = "/") -> List[SFTPFileDTO]:
        """List files and directories at the specified path."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(
                self._url("list"),
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
                self._url("download"),
                headers=self._header_builder(),
                json={"path": remote_path},
                timeout=300  # Downloads may take longer
            )
            raise_for_status_improved(response)
            return response.json()["packageId"]

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
                self._url("upload"),
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
                self._url("test"),
                headers=self._header_builder(),
                timeout=30
            )
            raise_for_status_improved(response)
            return response.json()
