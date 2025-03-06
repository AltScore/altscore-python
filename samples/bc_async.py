from altscore import AltScoreAsync as AltScore
from decouple import config
import asyncio


altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)
#%%
borrowers = asyncio.run(altscore.borrower_central.borrowers.summary_retrieve_all())
#%%
borrower = asyncio.run(altscore.borrower_central.borrowers.retrieve('d9898645-71cb-46b6-bc4f-deb920422569'))
# %%
b_data = asyncio.run(borrower.map_identities_and_fields_onto_dict(
    {
        "pdv_name": "identity.pdv_name",
        "nationality": "borrower_field.nationality"
    }
))
#%%