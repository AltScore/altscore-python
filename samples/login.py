from altscore import AltScore
from decouple import config
from altscore.altdata.schemas import InputKeys, SourceConfig

# With client_id and client_secret
altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment="staging"
)
# %%
source_data = altscore.altdata.requests.new_sync(
    input_keys=InputKeys(
        person_id="1714556493",
    ),
    sources_config=[
        SourceConfig(
            source_id="ECU_PUB_0002",
            version="v1"
        )
    ]
)
# %%
