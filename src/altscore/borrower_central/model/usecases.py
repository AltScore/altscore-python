from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class UsecasesAPDTO(BaseModel):
    id: str = Field(alias="id")
    name: str = Field(alias="name")
    description: str = Field(alias="description")
    root_task_instance_alias: str = Field(alias="rootTaskInstanceAlias")
    root_task_instance_input: Dict = Field(alias="rootTaskInstanceInput")
    task_instances: Dict = Field(alias="taskInstances")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }
    pass

class CreateUsecaseDTO(BaseModel):
    name: str = Field(alias="name")
    description: str = Field(alias="description")
    root_task_instance_alias: str = Field(alias="rootTaskInstanceAlias")
    root_task_instance_input: Dict = Field(alias="rootTaskInstanceInput")
    task_instances: Dict = Field(alias="taskInstances")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class UpdateUsecaseDTO(BaseModel):
    name: Optional[str] = Field(None, alias="name")
    description: Optional[str] = Field(None, alias="description")
    root_task_instance_alias: Optional[str] = Field(None, alias="rootTaskInstanceAlias")
    root_task_instance_input: Optional[Dict] = Field(None, alias="rootTaskInstanceInput")
    task_instances: Optional[Dict] = Field(None, alias="taskInstances")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class UsecasesSync(GenericSyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "usecases", header_builder, renew_token, UsecasesAPDTO.model_validate(data))

class UsecasesAsync(GenericAsyncResource):
    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "usecases", header_builder, renew_token, UsecasesAPDTO.model_validate(data))

class UsecasesSyncModule(GenericSyncModule):
    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=UsecasesSync,
                         retrieve_data_model=UsecasesAPDTO,
                         create_data_model=CreateUsecaseDTO,
                         update_data_model=UpdateUsecaseDTO,
                         resource="usecases")
        
class UsecasesAsyncModule(GenericAsyncModule):
        def __init__(self, altscore_client):
            super().__init__(altscore_client,
                            async_resource=UsecasesAsync,
                            retrieve_data_model=UsecasesAPDTO,
                            create_data_model=CreateUsecaseDTO,
                            update_data_model=UpdateUsecaseDTO,
                            resource="usecases")