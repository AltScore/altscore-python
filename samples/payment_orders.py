from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT"),
    partner_id="0b80ba71-fd36-426b-af72-3668aeeeaa01"
)
#%%
payment_orders = altscore.cms.payment_orders.query(
    reference_num="4109"
)
#%%