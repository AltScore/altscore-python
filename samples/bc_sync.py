from altscore import AltScore
from decouple import config

altscore = AltScore(api_key=config("ALTSCORE_API_KEY"), environment="staging")
# %%
borrower = altscore.borrower_central.borrowers.retrieve("48b8c289-b5c0-4cd4-a2d4-78489144067b")
# %%
documents = borrower.get_documents()
attachments = documents[0].get_attachments()
# %%
identities = borrower.get_identities(key="rfc")
i1 = identities[0].data.value
identities[0].data
# %%
executions = borrower.get_executions()
executions[0].data
# %%
new_data_model_id = altscore.borrower_central.data_models.create(
    {
        "key": "privacy_policy",
        "label": "Privacy Policy",
        "entityType": "authorization"
    }
)
# %%
data_models = altscore.borrower_central.data_models.query()
# %%
pc = borrower.get_points_of_contact(contact_method="phone", sort_by="priority", per_page=1)
# %%
legal_rep = borrower.get_relationships()
# %%
store_source_id = altscore.borrower_central.store_sources.create_altdata("MEX-PUB-0003", "v1")
#%%
store_source = altscore.borrower_central.store_sources.retrieve("AD_MEX-PUB-0003_v1")
# %%
store_package = altscore.borrower_central.store_packages.create(
    {
        "borrower_id": borrower.data.id,
        "source_id": "AD_MEX-PUB-0003_v1",
        "content": {"hello": "world"},
        "label": "test package",
    }
)
#%%
import datetime as dt

execution_id = altscore.borrower_central.executions.create(
    {
        "workflow_alias": "demo",
        "workflow_version": "v1"
    }
)
execution = altscore.borrower_central.executions.retrieve(execution_id)
execution.put_state(
    {
        "status": "pending",
        "callback_at": dt.datetime.now() + dt.timedelta(minutes=5),
        "state": {
            "message": "hello world again"
        }
    }
)
saved_state = execution.get_state()
saved_state.state["message"] = "hello world again x2"
execution.put_state(saved_state)
saved_state2 = execution.get_state()
assert saved_state.state["message"] == saved_state2.state["message"]
# %%
