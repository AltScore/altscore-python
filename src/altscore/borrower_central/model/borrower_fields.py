from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class BorrowerFieldAPIDTO(BaseModel):
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    value: Any = Field(alias="value")
    data_type: str = Field(alias="dataType")
    history: List[Dict] = Field(alias="history")
    tags: List[str] = Field(alias="tags", default=[])
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    key: str = Field(alias="key")
    value: str = Field(alias="value")
    data_type: str = Field(alias="dataType")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class UpdateBorrowerFieldDTO(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    form_id: Optional[str] = Field(alias="formId", default=None)
    reference_id: Optional[str] = Field(alias="referenceId", default=None)
    value: Optional[str] = Field(alias="value")
    data_type: Optional[str] = Field(alias="dataType")
    tags: List[str] = Field(alias="tags", default=[])

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class BorrowerFieldSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "borrower-fields", header_builder, renew_token, BorrowerFieldAPIDTO.parse_obj(data))


class BorrowerFieldsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=BorrowerFieldSync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")


class BorrowerFieldsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=BorrowerFieldAsync,
                         retrieve_data_model=BorrowerFieldAPIDTO,
                         create_data_model=CreateBorrowerFieldDTO,
                         update_data_model=UpdateBorrowerFieldDTO,
                         resource="borrower-fields")
