from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AttachmentAPIDTO(BaseModel):
    id: str = Field(alias="id")
    url: Optional[str] = Field(alias="url", default=None)
    label: Optional[str] = Field(alias="label", default=None)
    file_extension: Optional[str] = Field(alias="fileExtension", default=None)
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    created_at: str = Field(alias="createdAt", default=str)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class AttachmentInput(BaseModel):
    url: str = Field(alias="url")
    label: Optional[str] = Field(alias="label", default=None)
    file_extension: Optional[str] = Field(None, alias="fileExtension")
    metadata: Optional[dict] = Field(alias="metadata", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }
