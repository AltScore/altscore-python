from altscore import AltScore, borrower_sign_up_with_form
from decouple import config

# %%
altscore, borrower_id, form_id = borrower_sign_up_with_form(
    persona="individual",
    template_slug="whatsapp-landbot",
    tenant="arca",
    environment="staging"
)
# %%
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower_id,
        "key": "_whatsapp_customer_id",
        "value": "1234567"
    }
)
# %%
altscore.borrower_central.borrower_fields.create(
    {
        "borrowerId": borrower_id,
        "key": "_whatsapp_onboarding_current_step",
        "value": "1",
        "dataType": "number"
    }
)
# %%
borrower_id_found = altscore.borrower_central.forms.query_identity_lookup(
    form_id=form_id,
    key="_whatsapp_customer_id",
    value="1234",
    tenant="arca"
)
print(borrower_id_found.borrower_id)
# %%
value_found = altscore.borrower_central.forms.query_entity_value(
    borrower_id=borrower_id,
    entity_type="borrower_field",
    key="_whatsapp_onboarding_current_step"
)
#%%