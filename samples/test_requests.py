from altscore import AltScore
from decouple import config
from altscore.altdata.schemas import InputKeys, SourceConfig

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)
altscore_ad = AltScore(api_key=config("ALTSCORE_API_KEY_AD"))
# %%
borrower_id = altscore.borrower_central.borrowers.create(
    {
        "label": "Paulo Castro",
        "persona": "individual"
    }
)
# %%
identity_id = altscore.borrower_central.identities.create(
    {
        "borrower_id": borrower_id,
        "key": "name",
        "value": "Paulo Renato Castro Da Silva"
    }
)
# %%
borrower_id = "2d629d6e-8568-4833-b3a6-3307e61ee987"
borrower = altscore.borrower_central.borrowers.retrieve(borrower_id)
#%%
altscore.borrower_central.points_of_contact.create(
    {
        "borrower_id": borrower_id,
        "label": "email",
        "contact_method": "email",
        "value": "pp@pp.com"
    }
)
# %%
borrower.set_risk_rating("A1")
# %% Sync request
req1 = altscore_ad.altdata.requests.new_sync(
    input_keys=InputKeys(person_id="1714556493"),
    sources_config=[
        SourceConfig(source_id="ECU-PUB-0002", version="v1")
    ]
)
# %%
altscore.borrower_central.store_sources.create_altdata(altdata_source_id="ECU-PUB-0002", altdata_source_version="v1")
#%%
package_id = altscore.borrower_central.store_packages.create_from_altdata_request_result(
    borrower_id=borrower_id,
    source_id="ECU-PUB-0002",
    altdata_request_result=req1
)
#%%
packages = altscore.borrower_central.store_packages.query(borrower_id=borrower_id)
#%%
req1.are_all_source_calls_success()
req1.get_data("TES-GEN-0000").get("test0_reverseString", None)
# %%
req2 = altscore.altdata.requests.new_sync(
    input_keys={
        "personId": "1714556493"
    },
    sources_config=[
        {
            "sourceId": "ECU-PUB-0002",
            "version": "v1"
        }
    ]
)
# %%
req2_later = altscore.altdata.requests.retrieve(req2.request_id)
status2_later = req2_later.get_status()
response2_later = req2_later.pull()
package = response2_later.to_package("TES-GEN-0000")
# %%
