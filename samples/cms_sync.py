from altscore import AltScore
from decouple import config

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="sandbox")
# %%
me = altscore.partner_id
# %%
new_client = altscore.cms.clients.create(
    {
        "externalId": "test-123456789",
        "legalName": "Test Client S.A",
        "taxId": "123456789",
        "dba": "Test Client",
        "address": "Test Address",
        "emailAddress": "paulo@test.com"
    }
)
#%%
client = altscore.cms.clients.retrieve(client_identifier="test-123456789")
#%%
ca = client.get_credit_account(product_family="dpa")
#%%
ca.update(amount="100000.00", currency="ARS", reason="Línea inicial")
#%%
print(ca.data)