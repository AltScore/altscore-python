from altscore import AltScore
from decouple import config

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="sandbox")
# %%
me = altscore.partner_id
# %%
new_client = altscore.cms.clients.create(
    {
        "externalId": "test-12345678910",
        "legalName": "Test Client S.A",
        "taxId": "12345678910",
        "dba": "Test Client",
        "address": "Test Address",
        "emailAddress": "paulo@test.com"
    }
)
#%%
client = altscore.cms.clients.retrieve_by_external_id(external_id="test-123456789")
#%%
ca = client.get_credit_account(product_family="dpa")
#%%
ca.update(amount="100000.00", currency="ARS", reason="Línea inicial")
#%%
print(ca.data)
#%%
debts = altscore.cms.debts.retrieve_all()
#%%
active_debts = altscore.cms.debts.retrieve_all(status="active")
#%%
