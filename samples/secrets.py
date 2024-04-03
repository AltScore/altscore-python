from altscore import AltScore
from decouple import config
from altscore.altdata.schemas import InputKeys, SourceConfig
# With client_id and client_secret
altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment="staging"
)
#%%
secret = altscore.borrower_central.store_secrets.retrieve("workflows")
#%%