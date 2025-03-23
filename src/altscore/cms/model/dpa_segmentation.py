from typing import Optional,List
from pydantic import BaseModel, Field

class Rule(BaseModel):
    data_type: str = Field(alias="dataType")
    field: str = Field(alias="field")
    operator: str = Field(alias="operator")
    values: List[str] = Field(alias="values")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class RuleGroup(BaseModel):
    operator: str = Field(alias="operator")
    rules: list[Rule] = Field(alias="rules")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class RuleGroups(BaseModel):
    operator: str = Field(alias="operator")
    rule_group: RuleGroup = Field(alias="ruleGroup")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class RuleSet(BaseModel):
    name: str = Field(alias="name")
    rule_groups: list[RuleGroups] = Field(alias="ruleGroups")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class DPASegmentationAPIDTO(BaseModel):
    id: str = Field(alias="segmentationId")
    name: str = Field(alias="name")
    description: Optional[str] = Field(alias="description", default=None)
    rule_set: RuleSet = Field(alias="ruleSet")
    partner_id: str = Field(alias="partnerId")
    product_id: str = Field(alias="productId")
    created_at: str = Field(alias="createdAt")
    status: str = Field(alias="status")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    tenant: str = Field(alias="tenant")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class CreateDPASegmentationDTO(BaseModel):
    name: str = Field(alias="name")
    description: Optional[str] = Field(alias="description", default=None)
    rule_set: RuleSet = Field(alias="ruleSet")
    product_id: str = Field(alias="productId")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class UpdateDPASegmentationDTO(BaseModel):
    name: str = Field(alias="name")
    description: Optional[str] = Field(alias="description", default=None)
    rule_set: RuleSet = Field(alias="ruleSet")
    product_id: str = Field(alias="productId")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class SegmentationBase:
    def __init__(self, base_url):
        self.base_url = base_url


class SegmentationAsync(SegmentationBase):
    data: DPASegmentationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DPASegmentationAPIDTO):
        super().__init__(base_url)
        self.base_url = base_url
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.partner_id})"

class SegmentationSync(SegmentationBase):
    data: DPASegmentationAPIDTO

    def __init__(self, base_url, header_builder, renew_token, data: DPASegmentationAPIDTO):
        super().__init__(base_url)
        self._header_builder = header_builder
        self.renew_token = renew_token
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data.partner_id})"