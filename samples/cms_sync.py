from altscore import AltScore
from decouple import config

altscore = AltScore(client_id=config("ALTSCORE_CLIENT_ID"), client_secret=config("ALTSCORE_CLIENT_SECRET"),
                    environment=config("ALTSCORE_ENVIRONMENT"))
# %%
partners = altscore.cms.partners.query(limit=10)
# %%
new_client = altscore.cms.clients.create(
    {
        "externalId": "test-12345678910",
        "partnerId": partners[0].data.id,
        "legalName": "Test Client S.A",
        "taxId": "12345678910",
        "dba": "Test Client",
        "address": "Test Address",
        "emailAddress": "paulo@test.com"
    }
)
# %%
client = altscore.cms.clients.retrieve_by_external_id(external_id="test-12345678910",
                                                      partner_id=partners[0].data.id)
#%%
client.enable()
# %%
ca = client.get_credit_account(product_family="dpa")
# %%
ca.update(amount="100000.00", currency="ARS", reason="Línea inicial")
# %%
print(ca.data)
# %%
debts = altscore.cms.debts.retrieve_all()
# %%
active_debts = altscore.cms.debts.retrieve_all(status="active")
# %%
# partners = altscore.cms.partners.retrieve_all()
# %%
partner_to_change_settings = 'cf4d3a45-7178-482a-9b7c-3d71cbe91e2a'
# %%
updated_settings = altscore.cms.partners.update_dpa_settings(
    partner_id=partner_to_change_settings,
    settings={
        "onApproveFlowReserveAllAssignedAmount": True,
        "disbursement": "hello"
    }
)
#%%
