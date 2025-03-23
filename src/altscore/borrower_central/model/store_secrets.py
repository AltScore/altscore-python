from typing import Optional, Dict
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from pydantic import BaseModel, Field


class SecretAPIDTO(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    secret: Dict[str, str]

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateSecretDTO(BaseModel):
    id: Optional[str] = Field(alias="id", default=None)
    secret: Dict[str, str] = Field(alias="secret")
    ttl_minutes: Optional[int] = Field(alias="ttlMinutes", default=None)
    to_delete_at: Optional[str] = Field(alias="toDeleteAt", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class UpdateSecretDTO(BaseModel):
    secret: Dict[str, str] = Field(alias="secret")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class SecretSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/stores/secrets", header_builder, renew_token, SecretAPIDTO.model_validate(data))


class SecretAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/stores/secrets", header_builder, renew_token, SecretAPIDTO.model_validate(data))


class SecretsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=SecretSync,
                         retrieve_data_model=SecretAPIDTO,
                         create_data_model=CreateSecretDTO,
                         update_data_model=UpdateSecretDTO,
                         resource="stores/secrets")


class SecretsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=SecretAsync,
                         retrieve_data_model=SecretAPIDTO,
                         create_data_model=CreateSecretDTO,
                         update_data_model=UpdateSecretDTO,
                         resource="/stores/secrets")
