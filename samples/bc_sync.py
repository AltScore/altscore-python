from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)
# %%
# List all borrowers
borrower = altscore.borrower_central.borrowers.retrieve('d9898645-71cb-46b6-bc4f-deb920422569')
# %%
b_data = borrower.map_identities_and_fields_onto_dict(
    {
        "pdv_name": "identity.pdv_name",
        "nationality": "borrower_field.nationality"
    }
)
# %%
borrowers = altscore.borrower_central.borrowers.query_summary(
    per_page=1
)
# %%
import random

for i in range(34):
    b_id = altscore.borrower_central.borrowers.create(
        {
            "persona": "individual",
            "label": f"test-{random.randint(1, 1000)}",
        }
    )
    b = altscore.borrower_central.borrowers.retrieve(b_id)
    b.set_current_step(random.choice(["new", "pre_approved", "approved", "activated", "active"]))
# %%
b1 = altscore.borrower_central.borrowers.retrieve(borrowers[0].data.id)
i1 = b1.get_identities()
print(i1[1])
# %%
b1.set_current_step("new")
b1.set_risk_rating("A")
# %%
stage = b1.get_stage()
risk_rating = b1.get_risk_rating()
print(stage)
print(risk_rating)
# %%
borrower = altscore.borrower_central.borrowers.find_one_by_identity("full_name", "")
# %%
borrower1 = altscore.borrower_central.borrowers.query_summary(by="identity", search="Paulo")
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
# %%
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
# %%
rule = altscore.borrower_central.rules.retrieve_by_code("KYC-001")
alert = rule.data.get_alert_by_level(-1)
# %%
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