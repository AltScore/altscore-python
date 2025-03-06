import pandas as pd

from altscore import AltScoreAsync as AltScore
from altscore.utils import divide_in_chunks
from decouple import config
import asyncio

altscore = AltScore(user_token=config("ALTSCORE_USER_TOKEN"), environment="sandbox")
# %%
me = altscore.partner_id
# %%
all_clients = asyncio.run(altscore.cms.clients.retrieve_all())


# %%
async def get_credit_line(client):
    ca = await client.get_credit_account(product_family="dpa")
    return ca.data.dict(by_alias=True)


async def get_credit_lines(clients):
    return await asyncio.gather(*[get_credit_line(client) for client in clients])


# %%
clients_data = [e.data.dict(by_alias=True) for e in all_clients]
credit_lines_data = []
for chunk in divide_in_chunks(all_clients, 10):
    credit_lines_data.extend(asyncio.run(
        get_credit_lines(chunk)
    ))
# %%
clients_df = pd.DataFrame(clients_data)
credit_lines_df = pd.json_normalize(credit_lines_data)

cr_df = clients_df.merge(credit_lines_df, on="clientId", how="left")
# %%
