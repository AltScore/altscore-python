import httpx
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers


class PrintEntityRequest(BaseModel):
    """Request schema for printing an entity."""
    entity_type: str = Field(alias="entityType")
    entity_id: str = Field(alias="entityId")
    version: str = Field(alias="version", default="1")
    options: Optional[Dict[str, Any]] = Field(alias="options", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class EnrichedFieldValue(BaseModel):
    """Represents a field value enriched with data model metadata."""
    field_id: str = Field(alias="fieldId")
    key: str = Field(alias="key")
    label: Optional[str] = Field(alias="label", default=None)
    value: Any = Field(alias="value")
    data_type: str = Field(alias="dataType")
    tags: List[str] = Field(alias="tags", default=[])
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    allowed_values: Optional[List[Any]] = Field(alias="allowedValues", default=None)
    priority: Optional[int] = Field(alias="priority", default=None)
    order: Optional[int] = Field(alias="order", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class PrintEntityResponse(BaseModel):
    """Response schema for the print entity endpoint."""
    entity_type: str = Field(alias="entityType")
    entity_id: str = Field(alias="entityId")
    version: str = Field(alias="version")
    data: Dict[str, Any] = Field(alias="data")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

    def get_fields(self) -> List[EnrichedFieldValue]:
        """
        Parse and return the fields from the data as EnrichedFieldValue objects.
        Works for entity types that have a 'fields' list in their data.
        """
        fields_data = self.data.get("fields", [])
        return [EnrichedFieldValue.parse_obj(f) for f in fields_data]


class EntityPrintersSyncModule:
    """
    Module for printing entities in a format suitable for display/export.
    
    Example usage:
        # Print an asset
        result = altscore.borrower_central.entity_printers.print_entity(
            entity_type="asset",
            entity_id="asset-uuid-here"
        )
        print(result.data)  # The entity data
        
        # Get enriched fields
        fields = result.get_fields()
        for field in fields:
            print(f"{field.label}: {field.value}")
    """

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401
    def print_entity(
        self,
        entity_type: str,
        entity_id: str,
        version: str = "1",
        options: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> PrintEntityResponse:
        """
        Print an entity's data in a format suitable for printing/export.
        
        Args:
            entity_type: The type of entity to print (e.g., "asset")
            entity_id: The ID of the entity to print
            version: The version of the print format (default: "1")
            options: Optional configuration options for printing
            timeout: Request timeout in seconds
            
        Returns:
            PrintEntityResponse containing the print-friendly entity data
        """
        url = f"{self.altscore_client._borrower_central_base_url}/v1/internal/entity-printers/print"
        
        request_data = PrintEntityRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            version=version,
            options=options
        )
        
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self.build_headers(),
                json=request_data.dict(by_alias=True, exclude_none=True),
                timeout=timeout
            )
            raise_for_status_improved(response)
            return PrintEntityResponse.parse_obj(response.json())


class EntityPrintersAsyncModule:
    """
    Async module for printing entities in a format suitable for display/export.
    
    Example usage:
        # Print an asset
        result = await altscore.borrower_central.entity_printers.print_entity(
            entity_type="asset",
            entity_id="asset-uuid-here"
        )
        print(result.data)  # The entity data
        
        # Get enriched fields
        fields = result.get_fields()
        for field in fields:
            print(f"{field.label}: {field.value}")
    """

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401_async
    async def print_entity(
        self,
        entity_type: str,
        entity_id: str,
        version: str = "1",
        options: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> PrintEntityResponse:
        """
        Print an entity's data in a format suitable for printing/export.
        
        Args:
            entity_type: The type of entity to print (e.g., "asset")
            entity_id: The ID of the entity to print
            version: The version of the print format (default: "1")
            options: Optional configuration options for printing
            timeout: Request timeout in seconds
            
        Returns:
            PrintEntityResponse containing the print-friendly entity data
        """
        url = f"{self.altscore_client._borrower_central_base_url}/v1/internal/entity-printers/print"
        
        request_data = PrintEntityRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            version=version,
            options=options
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.build_headers(),
                json=request_data.dict(by_alias=True, exclude_none=True),
                timeout=timeout
            )
            raise_for_status_improved(response)
            return PrintEntityResponse.parse_obj(response.json())
