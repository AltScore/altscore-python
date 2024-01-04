from altscore import AltScore
from decouple import config

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="sandbox", async_mode=True)
# %%
me = altscore.partner_id
# %%
