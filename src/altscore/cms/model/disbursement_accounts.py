from typing import Optional

from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    account_number: str = Field(alias="accountNumber")
    bank_name: str = Field(alias="bankName")
    bank_code: str = Field(alias="bankCode")
    account_type: int = Field(alias="accountType")

class DisbursementAccountBaseModel(BaseModel):
    id: str = Field(alias="accountId")
    name: str = Field(alias="name")
    phone: Optional[str] = Field(alias="phone", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    tax_id: str = Field(alias="taxId")
    partner_id: str = Field(alias="partnerId")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    type: str = Field(alias="type")
    bank_account: BankAccount = Field(alias="bankAccount")
    status: str = Field(alias="status")

class DisbursementClientAccountAPIDTO(DisbursementAccountBaseModel):
    client_id: str = Field(alias="clientId")
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True

class DisbursementPartnerAccountAPIDTO(DisbursementAccountBaseModel):
    payment_concept_template: Optional[str] = Field(alias="paymentConceptTemplate", default=None)
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True

class CreateDisbursementClientAccountDTO(BaseModel):
    client_id: str = Field(alias="id")
    partner_id: str = Field(alias="partnerId")
    email_address: Optional[str] = Field(alias="email", default=None)
    phone_number: Optional[str] = Field(alias="phone", default=None)
    bank_account: BankAccount = Field(alias="bankAccount")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True

class CreateDisbursementPartnerAccountDTO(BaseModel):
    name: str = Field(alias="name")
    tax_id: str = Field(alias="taxId")
    partner_id: str = Field(alias="partnerId")
    payment_concept_template: Optional[str] = Field(alias="paymentConceptTemplate",default=None)
    bank_account: BankAccount = Field(alias="bankAccount")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True
