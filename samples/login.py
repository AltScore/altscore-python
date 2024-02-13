from altscore import AltScore
from decouple import config

# With client_id and client_secret
altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment="production"
)
# %%
altscore.get_tenant_from_token()
# %%
req1 = altscore.altdata.requests.new_sync(
    input_keys={"personId": "1234567890"},
    sources_config=[
        {
            "sourceId": "TES-GEN-0000",
            "version": "v1"
        }
    ],
    timeout=10
)
# %%
