from altscore import AltScore
from decouple import config

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="sandbox")
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
    }
)
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower_id,
        "key": "rfc",
        "value": "XAXX010101000",
    }
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
    legal_name_identity_key="full_name",
    tax_id_identity_key="rfc",
    partner_id="ed04ca1d-b4bd-47a3-995f-785e76a81937"
)
# %%
