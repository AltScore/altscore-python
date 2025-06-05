from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from altscore.borrower_central.model.accounting_amount import Amount


class LineItemAPIDTO(BaseModel):
    id: str = Field(alias="id")
    accounting_document_id: str = Field(alias="accountingDocumentId")
    item_code: Optional[str] = Field(default=None, alias="itemCode",
                                     description="Item code, if the item is not an stockable with sku")
    sku: Optional[str] = Field(default=None, alias="sku", description="Product / material code")
    description: Optional[str] = Field(default=None, alias="description")
    qty: Optional[str] = Field(default=None, alias="qty", description="Quantity involved")
    unit_price: Optional[str] = Field(default=None, alias="unitPrice")
    unit_price_currency: Optional[str] = Field(default=None, alias="unitPriceCurrency")
    amount: Optional[Dict[str, Any]] = Field(default=None, alias="amount", description="amount")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")
    parsed_raw: Optional[Dict[str, Any]] = Field(default=None, alias="parsedRaw")
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")
    # Variance
    is_variance: Optional[bool] = Field(default=None, alias="isVariance")
    variance_kind: Optional[str] = Field(
        default=None,
        alias="varianceKind",
        description="PRICE or QUANTITY"
    )
    reference_unit_price: Optional[str] = Field(
        default=None, alias="referenceUnitPrice",
        description="Price from PO / contract (for PRICE variance)"
    )
    reference_price: Optional[str] = Field(
        default=None, alias="referencePrice",
        description="Price from PO / contract (for PRICE variance)"
    )
    reference_qty: Optional[str] = Field(
        default=None, alias="referenceQty",
        description="Expected quantity (for QUANTITY variance)"
    )
    # Return
    is_return: Optional[bool] = Field(default=None, alias="isReturn")
    reason_code: Optional[str] = Field(
        default=None, alias="reasonCode",
        description="Damaged, expired, decomiso, etc."
    )
    # Rebate - Acuerdos Comerciales
    is_rebate: Optional[bool] = Field(default=None, alias="isRebate")
    agreement_id: Optional[str] = Field(
        default=None, alias="agreementId",
        description="ID of trade-promotion / rebate contract"
    )
    period_start: Optional[str] = Field(
        default=None, alias="periodStart",
        description="Start of accrual period (yyyy-mm-dd)"
    )
    period_end: Optional[str] = Field(
        default=None, alias="periodEnd",
        description="End of accrual period (yyyy-mm-dd)"
    )

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CreateLineItemDTO(BaseModel):
    accounting_document_id: str = Field(alias="accountingDocumentId")
    sku: Optional[str] = Field(alias="sku", default=None)
    item_code: Optional[str] = Field(alias="itemCode", default=None)
    description: Optional[str] = Field(alias="description")
    qty: Optional[str] = Field(alias="qty", default=None)
    unit_price: Optional[str] = Field(alias="unitPrice", default=None)
    unit_price_currency: Optional[str] = Field(alias="unitPriceCurrency", default=None)
    amount: Optional[Amount] = Field(alias="amount", default=None)
    parsed_raw: Optional[Dict[str, Any]] = Field(default=None, alias="parsedRaw")
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)
    # Variance
    is_variance: Optional[bool] = Field(alias="isVariance", default=None)
    variance_kind: Optional[str] = Field(alias="varianceKind", default=None)
    reference_unit_price: Optional[str] = Field(alias="referenceUnitPrice", default=None)
    reference_price: Optional[str] = Field(alias="referencePrice", default=None)
    reference_qty: Optional[str] = Field(alias="referenceQty", default=None)
    # Return
    is_return: Optional[bool] = Field(alias="isReturn", default=None)
    reason_code: Optional[str] = Field(alias="reasonCode", default=None)
    # Rebate
    is_rebate: Optional[bool] = Field(alias="isRebate", default=None)
    agreement_id: Optional[str] = Field(alias="agreementId", default=None)
    period_start: Optional[str] = Field(alias="periodStart", default=None)
    period_end: Optional[str] = Field(alias="periodEnd", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class UpdateLineItemDTO(BaseModel):
    sku: Optional[str] = Field(alias="sku", default=None)
    item_code: Optional[str] = Field(alias="itemCode", default=None)
    description: Optional[str] = Field(alias="description")
    qty: Optional[str] = Field(alias="qty", default=None)
    unit_price: Optional[str] = Field(alias="unitPrice", default=None)
    unit_price_currency: Optional[str] = Field(alias="unitPriceCurrency", default=None)
    amount: Optional[Amount] = Field(alias="amount", default=None)
    parsed_raw: Optional[Dict[str, Any]] = Field(default=None, alias="parsedRaw")
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)
    # Variance
    is_variance: Optional[bool] = Field(alias="isVariance", default=None)
    variance_kind: Optional[str] = Field(alias="varianceKind", default=None)
    reference_unit_price: Optional[str] = Field(alias="referenceUnitPrice", default=None)
    reference_price: Optional[str] = Field(alias="referencePrice", default=None)
    reference_qty: Optional[str] = Field(alias="referenceQty", default=None)
    # Return
    is_return: Optional[bool] = Field(alias="isReturn", default=None)
    reason_code: Optional[str] = Field(alias="reasonCode", default=None)
    # Rebate
    is_rebate: Optional[bool] = Field(alias="isRebate", default=None)
    agreement_id: Optional[str] = Field(alias="agreementId", default=None)
    period_start: Optional[str] = Field(alias="periodStart", default=None)
    period_end: Optional[str] = Field(alias="periodEnd", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True



class LineItemSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "accounting/line-items", header_builder,
                         renew_token, LineItemAPIDTO.parse_obj(data))


class LineItemAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "accounting/line-items", header_builder,
                         renew_token, LineItemAPIDTO.parse_obj(data))


class LineItemsSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=LineItemSync,
                         retrieve_data_model=LineItemAPIDTO,
                         create_data_model=CreateLineItemDTO,
                         update_data_model=UpdateLineItemDTO,
                         resource="accounting/line-items")


class LineItemsAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=LineItemAsync,
                         retrieve_data_model=LineItemAPIDTO,
                         create_data_model=CreateLineItemDTO,
                         update_data_model=UpdateLineItemDTO,
                         resource="accounting/line-items")

