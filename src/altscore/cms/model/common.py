from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any


class DisbursementSettings(BaseModel):
    disburse_to: str = Field(alias="disburseTo")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class Money(BaseModel):
    amount: str
    currency: str

    @field_validator("amount", mode="before")
    def convert_amount_to_str(cls, value: Any) -> str:
        if isinstance(value, int):
            return f"{value:.2f}"
        elif isinstance(value, float):
            return f"{value:.2f}"
        elif not isinstance(value, str):
            raise TypeError("amount must be a string or an integer")
        return value


class ScheduleOriginalAmounts(BaseModel):
    fees: Money = Field(alias="fees")
    interest: Money = Field(alias="interest")
    principal: Money = Field(alias="principal")
    taxes: Money = Field(alias="taxes")
    total: Money = Field(alias="total")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class Schedule(BaseModel):
    due_date: str = Field(alias="dueDate")
    number: int = Field(alias="number")
    original_amounts: ScheduleOriginalAmounts = Field(alias="originalAmounts")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True  # Allows automatic type conversion
    }

    @field_validator("number", mode="before")
    def convert_number_to_str(cls, value: Any) -> str:
        if isinstance(value, int):
            return f"{value:.2f}"
        elif isinstance(value, float):
            return f"{value:.2f}"
        elif not isinstance(value, str):
            raise TypeError("number must be a string or an integer")
        return value



class InterestRate(BaseModel):
    period: int = Field(alias="period")
    rate: str = Field(alias="rate")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True  # Allows automatic type conversion
    }


class TermsPenalties(BaseModel):
    charge_code: str = Field(alias="chargeCode")
    compute_every: int = Field(alias="computeEvery")
    enabled: Optional[bool] = Field(None, alias="enabled")
    grace_period: int = Field(alias="gracePeriod")
    rate: InterestRate = Field(alias="rate")
    times_to_compute: int = Field(alias="timesToCompute")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True  # Allows automatic type conversion
    }


class TermsFees(BaseModel):
    amount: Optional[Money] = Field(None, alias="amount")
    amount_rate: Optional[str] = Field(None, alias="amountRate")
    calculation_type: Optional[str] = Field(None, alias="calculationType")
    description: Optional[str] = Field(None, alias="description")
    name: Optional[str] = Field(None, alias="name")
    tax: Optional[int] = Field(None, alias="tax")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True  # Allows automatic type conversion
    }


class Terms(BaseModel):
    amortization_type: str = Field(alias="amortizationType")
    disbursement_date: Optional[str] = Field(None, alias="disbursementDate")
    installments: int = Field(alias="installments")
    fees: Optional[List[Optional[TermsFees]]] = Field(alias="fees", default=None)
    interest_calculate_type: str = Field(alias="interestCalculateType")
    interest_rate: InterestRate = Field(alias="interestRate")
    interest_tax: float = Field(alias="interestTax")
    principal: Optional[Money] = Field(None, alias="principal")
    repayEvery: int = Field(alias="repayEvery")
    sub_total_amount: Optional[Money] = Field(alias="subTotalAmount", default=None)
    penalties: Optional[List[TermsPenalties]] = Field(alias="penalties", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    calendar_type: Optional[str] = Field(alias="calendarType", default=None)
    loan_term_duration: Optional[int] = Field(alias="loanTermDuration", default=None)
    disbursement_settings: Optional[DisbursementSettings] = Field(alias="disbursementSettings", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True  # Allows automatic type conversion
    }
