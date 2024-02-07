from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class RuleAlert(BaseModel):
    level: int = Field(alias="level")
    message: str = Field(alias="message")


class RuleAPIDTO(BaseModel):
    id: str = Field(alias="id")
    code: str = Field(alias="code")
    label: str = Field(alias="label")
    alerts: List[RuleAlert] = Field(alias="alerts", default=[])
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateRuleDTO(BaseModel):
    label: str = Field(alias="label")
    code: str = Field(alias="code")
    alerts: List[RuleAlert] = Field(alias="alerts")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class RulesSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "rules", header_builder, renew_token, RuleAPIDTO.parse_obj(data))


class RulesAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "rules", header_builder, renew_token, RuleAPIDTO.parse_obj(data))


class RulesSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=RulesSync,
                         retrieve_data_model=RuleAPIDTO,
                         create_data_model=CreateRuleDTO,
                         update_data_model=CreateRuleDTO,
                         resource="rules")


class RulesAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=RulesAsync,
                         retrieve_data_model=RuleAPIDTO,
                         create_data_model=CreateRuleDTO,
                         update_data_model=CreateRuleDTO,
                         resource="rules")
