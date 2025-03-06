from altscore import AltScore
from decouple import config
# With client_id and client_secret
altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)
#%%
secret = altscore.borrower_central.store_secrets.retrieve("workflows")
#%%
borrowers = altscore.borrower_central.borrowers.query_summary(per_page=100)