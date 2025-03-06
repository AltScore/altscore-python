from altscore import AltScore
from altscore.altdata.schemas import SourceConfig
import pandas as pd
from decouple import config

altscore = AltScore(api_key=config("ALTSCORE_API_KEY"))

# %%
data = [
    {"personId": "test12345"},
    {"personId": "12345test"},
    {"personId": "aaaaabbbb"},
    {"personId": "0987654321"},
    {"personId": "123"},
    {"personId": "333"},
    {"personId": "222"},
    {"personId": "a22"},
    {"personId": "b22"},
    {"personId": "c22"},
]
input_df = pd.DataFrame(data)
my_batch = altscore.altdata.batches.new_batch_from_dataframe(
    df=input_df,
    label="test_batch",
    sources_config=[
        SourceConfig(source_id="TES-GEN-0000", version="v1")
    ]
)
# %%
print(my_batch.batch_id)
my_batch.get_status()
my_batch.status.print_source_stats()
df_out = my_batch.export_to_dataframe()
# %%

my_batch1 = altscore.altdata.batches.retrieve("3809dab7-39e2-49bf-9626-e36a75efeecc")
my_batch1.get_status()
print(my_batch1.status)
my_batch1.status.print_source_stats()
df_out1 = my_batch1.export_to_dataframe()
data_out1 = my_batch1.export_source_data_to_dict()

# %%
