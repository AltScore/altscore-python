from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    source_id: str = Field(alias="sourceId")
    version: str = Field(alias="version")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }
