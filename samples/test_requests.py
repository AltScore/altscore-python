from altscore import AltScore
from decouple import config
from altscore.altdata.schemas import InputKeys, SourceConfig

altscore = AltScore(api_key=config("ALTSCORE_API_KEY"))

# %% Sync request
req1 = altscore.altdata.request.new_sync(
    input_keys=InputKeys(person_id="test123"),
    sources_config=[
        SourceConfig(source_id="TES-GEN-0000", version="v1")
    ]
)
# %%
req1.are_all_source_calls_success()
req1.get_data("TES-GEN-0000").get("test0_reverseString", None)
# %%
req2 = altscore.altdata.request.new_async(
    input_keys=InputKeys(person_id="test123"),
    sources_config=[
        SourceConfig(source_id="TES-GEN-0000", version="v1")
    ]
)
#%%
req2_later = altscore.altdata.request.retrieve(req2.request_id)
status2_later = req2_later.get_status()
response2_later = req2_later.pull()
package = response2_later.to_package("TES-GEN-0000")
# %%
