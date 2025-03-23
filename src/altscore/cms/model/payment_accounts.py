from typing import List, Optional
from pydantic import BaseModel, Field


class AccountHolder(BaseModel):
    client_id: str = Field(alias="clientId")
    partner_id: str = Field(alias="partnerId")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class Reference(BaseModel):
    account_reference_id: str = Field(alias="accountReferenceId")
    gateway_id: str = Field(alias="gatewayId")
    provider: str = Field(alias="provider")
    reference: str = Field(alias="reference")
    status: str = Field(alias="status")
    created_at: str = Field(alias="createdAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class PaymentAccountAPIDTO(BaseModel):
    account_id: str = Field(alias="accountId")
    account_holder: AccountHolder = Field(alias="accountHolder")
    references: Optional[List[Reference]] = Field(alias="references", default=[])
    created_at: str = Field(alias="createdAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

    def get_active_references_by_provider(self, provider: str):
        return [reference for reference in self.references if
                reference.provider == provider and reference.status == "ACTIVE"]


class CreatePaymentAccountDTO(BaseModel):
    partner_id: str = Field(alias="partnerId")
    client_id: str = Field(alias="clientId")
    auto_create_references: bool = Field(alias="autoCreateReferences", default=True)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreatePaymentReferenceDTO(BaseModel):
    provider: Optional[str] = Field(alias="provider", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }
