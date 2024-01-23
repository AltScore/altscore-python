from altscore import AltScore
from decouple import config

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="staging")
# %%
altscore.borrower_central.data_models.create(
    {
        "key": "rfc",
        "label": "RFC",
        "entity_type": "identity",
        "priority": 1
    },
    update_if_exists=True
)
altscore.borrower_central.data_models.create(
    {
        "key": "full_name",
        "label": "Full Name",
        "entity_type": "identity",
        "priority": -1
    },
    update_if_exists=True
)
altscore.borrower_central.data_models.create(
    {
        "key": "id_pdv_arca",
        "label": "PDV ID ARCA",
        "entity_type": "identity",
        "priority": -1
    },
    update_if_exists=True
)# %%
partners = altscore.cms.partners.retrieve_all()
if len(partners) == 0:
    partner_id = altscore.cms.partners.create(
        {
            "name": "Im Lender",
            "shortName": "lender",
            "email": "lender@lender.ai",
            "taxId": "XAXX010101000"
        }
    )
else:
    partner_id = partners[0].data.id
# %%
borrower_id = altscore.borrower_central.borrowers.create(
    {
        "persona": "individual",
        "label": "Jose Perez",
    }
)

altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower_id,
        "key": "full_name",
        "value": "Jose Perez",
    },
)
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower_id,
        "key": "rfc",
        "value": "XAXX010101000",
    },
)
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower_id,
        "key": "id_pdv_arca",
        "value": "55555",
    },
)
altscore.borrower_central.addresses.create(
    {
        "borrowerId": borrower_id,
        "street1": "Calle 134",
        "country": "MEX",
        "state": "MX-AGU",
        "city": "Aguascalientes",
        "zipCode": "20100"
    }
)
altscore.borrower_central.points_of_contact.create(
    {
        "borrower_id": borrower_id,
        "contact_method": "email",
        "value": "jose@example.com"
    }
)
altscore.borrower_central.points_of_contact.create(
    {
        "borrower_id": borrower_id,
        "contact_method": "phone",
        "value": "4491234567"
    }
)
# %%
cms_id = altscore.new_cms_client_from_borrower(
    borrower_id=borrower_id,
    external_id_identity_key="pdv_id",
    legal_name_identity_key="full_name",
    tax_id_identity_key="rfc",
    partner_id=partner_id
)
# %%
client = altscore.cms.clients.retrieve(cms_id)
#%%
ca = client.get_credit_account(product_family="dpa")
#%%
ca.data.is_enabled()
#%%
client = altscore.cms.clients.retrieve_by_external_id(external_id="55555", partner_id=partner_id)
#%%