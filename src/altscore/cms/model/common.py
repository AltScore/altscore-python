from pydantic import BaseModel, Field
from typing import Optional, List


class Money(BaseModel):
    amount: str
    currency: str


class ScheduleOriginalAmounts(BaseModel):
    fees: Money = Field(alias="fees")
    interest: Money = Field(alias="interest")
    principal: Money = Field(alias="principal")
    taxes: Money = Field(alias="taxes")
    total: Money = Field(alias="total")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Schedule(BaseModel):
    due_date: str = Field(alias="dueDate")
    number: int = Field(alias="number")
    original_amounts: ScheduleOriginalAmounts = Field(alias="originalAmounts")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class InterestRate(BaseModel):
    period: int = Field(alias="period")
    rate: str = Field(alias="rate")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class TermsPenalties(BaseModel):
    charge_code: str = Field(alias="chargeCode")
    compute_every: int = Field(alias="computeEvery")
    enabled: Optional[bool] = Field(None, alias="enabled")
    grace_period: int = Field(alias="gracePeriod")
    rate: InterestRate = Field(alias="rate")
    times_to_compute: int = Field(alias="timesToCompute")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True


class Terms(BaseModel):
    amortization_type: str = Field(alias="amortizationType")
    disbursement_date: Optional[str] = Field(alias="disbursementDate")
    installments: int = Field(alias="installments")
    interest_calculate_type: str = Field(alias="interestCalculateType")
    interest_rate: InterestRate = Field(alias="interestRate")
    interest_tax: int = Field(alias="interestTax")
    principal: Optional[Money] = Field(alias="principal")
    repayEvery: int = Field(alias="repayEvery")
    sub_total_amount: Optional[Money] = Field(alias="subTotalAmount", default=None)
    penalties: Optional[List[TermsPenalties]] = Field(alias="penalties", default=None)
    name: Optional[str] = Field(alias="name", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        populate_by_alias = True
