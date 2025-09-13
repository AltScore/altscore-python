from typing import List, Optional, Dict, Any, Union

import httpx
from pydantic import BaseModel, Field, validator

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


# Request DTOs for new file operations
class SFTPDeleteRequest(BaseModel):
    path: str = Field(min_length=1)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPMoveRequest(BaseModel):
    source_path: str = Field(alias="sourcePath", min_length=1)
    destination_path: str = Field(alias="destinationPath", min_length=1)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPMkdirRequest(BaseModel):
    path: str = Field(min_length=1)
    mode: Optional[int] = Field(default=755, ge=0, le=777)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPStatRequest(BaseModel):
    path: str = Field(min_length=1)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPCopyRequest(BaseModel):
    source_path: str = Field(alias="sourcePath", min_length=1)
    destination_path: str = Field(alias="destinationPath", min_length=1)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPBulkDeleteRequest(BaseModel):
    paths: List[str] = Field(min_items=1, max_items=50)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


# Response DTOs for new file operations
class SFTPDeleteResponse(BaseModel):
    path: str
    operation: str  # "remove" for files, "rmdir" for directories
    success: bool
    message: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPMoveResponse(BaseModel):
    source_path: str = Field(alias="sourcePath")
    destination_path: str = Field(alias="destinationPath")
    operation: str
    success: bool
    message: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPMkdirResponse(BaseModel):
    path: str
    mode: str
    operation: str
    success: bool
    message: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPStatResponse(BaseModel):
    path: str
    name: str
    size: Optional[int] = None
    permissions: Optional[str] = None
    uid: Optional[int] = None
    gid: Optional[int] = None
    is_directory: bool = Field(alias="isDirectory")
    is_file: bool = Field(alias="isFile")
    is_symlink: bool = Field(alias="isSymlink")
    modified_at: Optional[str] = Field(alias="modifiedAt", default=None)
    accessed_at: Optional[str] = Field(alias="accessedAt", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPCopyResponse(BaseModel):
    source_path: str = Field(alias="sourcePath")
    destination_path: str = Field(alias="destinationPath")
    operation: str  # "copy_file" for files, "copy_directory" for directories
    success: bool
    message: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPBulkDeleteOperationResult(BaseModel):
    path: str
    operation: str  # "remove", "rmdir", "skip", "error"
    success: bool
    message: str
    error_type: Optional[str] = Field(alias="errorType", default=None)
    error_message: Optional[str] = Field(alias="errorMessage", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class SFTPBulkDeleteResponse(BaseModel):
    operation: str  # Always "bulk_delete"
    total_paths: int = Field(alias="totalPaths")
    successful_count: int = Field(alias="successfulCount")
    failed_count: int = Field(alias="failedCount")
    success: bool
    message: str
    successful: List[SFTPBulkDeleteOperationResult]
    failed: List[SFTPBulkDeleteOperationResult]

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

    @retry_on_401
    def delete_file(self, path: str) -> SFTPDeleteResponse:
        """Delete a file or directory from the SFTP server."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("delete-file"),
                headers=self._header_builder(),
                json={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPDeleteResponse.parse_obj(response.json())

    @retry_on_401
    def move_file(self, source_path: str, destination_path: str) -> SFTPMoveResponse:
        """Move or rename a file/directory on the SFTP server."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("move"),
                headers=self._header_builder(),
                json={"sourcePath": source_path, "destinationPath": destination_path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPMoveResponse.parse_obj(response.json())

    @retry_on_401
    def create_directory(self, path: str, mode: Optional[int] = 755) -> SFTPMkdirResponse:
        """Create a directory on the SFTP server."""
        payload = {"path": path}
        if mode is not None:
            # Validate mode is in proper range
            if not isinstance(mode, int) or mode < 0 or mode > 777:
                raise ValueError(f"Invalid mode: {mode}. Mode must be an integer between 0 and 777")
            # Convert to octal string format as server may expect string representation
            payload["mode"] = oct(mode)

        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("mkdir"),
                headers=self._header_builder(),
                json=payload,
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPMkdirResponse.parse_obj(response.json())

    @retry_on_401
    def get_file_info(self, path: str) -> SFTPStatResponse:
        """Get detailed information about a file or directory."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("stat"),
                headers=self._header_builder(),
                json={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPStatResponse.parse_obj(response.json())

    @retry_on_401
    def copy_file(self, source_path: str, destination_path: str) -> SFTPCopyResponse:
        """Copy a file or directory on the SFTP server. For directories, performs recursive copy."""
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("copy"),
                headers=self._header_builder(),
                json={"sourcePath": source_path, "destinationPath": destination_path},
                timeout=300  # Copy operations may take longer, especially for large directories
            )
            raise_for_status_improved(response)
            return SFTPCopyResponse.parse_obj(response.json())

    @retry_on_401
    def bulk_delete(self, paths: List[str]) -> SFTPBulkDeleteResponse:
        """Delete multiple files and/or directories from the SFTP server in parallel.
        
        Args:
            paths: List of file/directory paths to delete (1-50 items)
            
        Returns:
            SFTPBulkDeleteResponse with detailed results for each path
            
        Note:
            - Processes up to 10 delete operations simultaneously
            - Files not found are reported as success (idempotent behavior)  
            - Individual errors don't stop processing of remaining paths
        """
        if not paths:
            raise ValueError("paths list cannot be empty")
        if len(paths) > 50:
            raise ValueError("Maximum 50 paths allowed per bulk delete request")
            
        with httpx.Client(base_url=self.base_url) as client:
            response = client.post(
                self._url("bulk-delete"),
                headers=self._header_builder(),
                json={"paths": paths},
                timeout=300  # Bulk operations may take longer
            )
            raise_for_status_improved(response)
            return SFTPBulkDeleteResponse.parse_obj(response.json())


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

    @retry_on_401_async
    async def delete_file(self, path: str) -> SFTPDeleteResponse:
        """Delete a file or directory from the SFTP server."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("delete-file"),
                headers=self._header_builder(),
                json={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPDeleteResponse.parse_obj(response.json())

    @retry_on_401_async
    async def move_file(self, source_path: str, destination_path: str) -> SFTPMoveResponse:
        """Move or rename a file/directory on the SFTP server."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("move"),
                headers=self._header_builder(),
                json={"sourcePath": source_path, "destinationPath": destination_path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPMoveResponse.parse_obj(response.json())

    @retry_on_401_async
    async def create_directory(self, path: str, mode: Optional[int] = 755) -> SFTPMkdirResponse:
        """Create a directory on the SFTP server."""
        payload = {"path": path}
        if mode is not None:
            # Validate mode is in proper range
            if not isinstance(mode, int) or mode < 0 or mode > 777:
                raise ValueError(f"Invalid mode: {mode}. Mode must be an integer between 0 and 777")
            # Convert to octal string format as server may expect string representation
            payload["mode"] = oct(mode)

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("mkdir"),
                headers=self._header_builder(),
                json=payload,
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPMkdirResponse.parse_obj(response.json())

    @retry_on_401_async
    async def get_file_info(self, path: str) -> SFTPStatResponse:
        """Get detailed information about a file or directory."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("stat"),
                headers=self._header_builder(),
                json={"path": path},
                timeout=120
            )
            raise_for_status_improved(response)
            return SFTPStatResponse.parse_obj(response.json())

    @retry_on_401_async
    async def copy_file(self, source_path: str, destination_path: str) -> SFTPCopyResponse:
        """Copy a file or directory on the SFTP server. For directories, performs recursive copy."""
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("copy"),
                headers=self._header_builder(),
                json={"sourcePath": source_path, "destinationPath": destination_path},
                timeout=300  # Copy operations may take longer, especially for large directories
            )
            raise_for_status_improved(response)
            return SFTPCopyResponse.parse_obj(response.json())

    @retry_on_401_async
    async def bulk_delete(self, paths: List[str]) -> SFTPBulkDeleteResponse:
        """Delete multiple files and/or directories from the SFTP server in parallel.
        
        Args:
            paths: List of file/directory paths to delete (1-50 items)
            
        Returns:
            SFTPBulkDeleteResponse with detailed results for each path
            
        Note:
            - Processes up to 10 delete operations simultaneously
            - Files not found are reported as success (idempotent behavior)  
            - Individual errors don't stop processing of remaining paths
        """
        if not paths:
            raise ValueError("paths list cannot be empty")
        if len(paths) > 50:
            raise ValueError("Maximum 50 paths allowed per bulk delete request")
            
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                self._url("bulk-delete"),
                headers=self._header_builder(),
                json={"paths": paths},
                timeout=300  # Bulk operations may take longer
            )
            raise_for_status_improved(response)
            return SFTPBulkDeleteResponse.parse_obj(response.json())
