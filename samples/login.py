from altscore import AltScore
from decouple import config

# With client_id and client_secret
altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment="staging"
)
# %%
altscore.get_tenant_from_token()
# %%
