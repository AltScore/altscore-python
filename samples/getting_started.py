from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)

#%%
data_models = altscore.borrower_central.data_models.retrieve_all()
#%%
# List borrowers
borrowers = altscore.borrower_central.borrowers.query()
# List borrowers summary
borrowers_summary = altscore.borrower_central.borrowers.query_summary()
#%%
# Create a borrower
altscore.borrower_central.borrowers.create(
    {
        "label": "Juan Perez 2",
        "persona": "individual"
    }
)
#%%
# Create a borrower
altscore.borrower_central.borrowers.create(
    {
        "label": "Ivan Mena",
        "flag": "red",
        "persona": "individual"
    }
)
#%%
borrower = borrowers[0]