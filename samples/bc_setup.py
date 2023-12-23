from altscore import AltScore
from decouple import config

altscore = AltScore(api_key=config("ALTSCORE_API_KEY"), environment="staging")
# %%
data_models = [
    {
        "key": "privacy_policy",
        "label": "Política de Privacidad",
        "entityType": "authorization"
    },
    {
        "key": "terms_and_conditions",
        "label": "Terminos y Condiciones",
        "entityType": "authorization"
    },
    {
        "key": "bureau_query",
        "label": "Autorización para consulta de Buró",
        "entityType": "authorization"
    },
    {
        "key": "_whatsapp_onboarding_current_step",
        "label": "Paso actual de Onboarding WhatsApp (1-6)",
        "entityType": "borrower_field"
    },
    {
        "key": "changarro_id",
        "label": "ID de Changarro",
        "entityType": "borrower_field"
    },
    {
        "key": "rfc",
        "label": "RFC",
        "entityType": "identity",
        "priority": 1
    },
    {
        "key": "curp",
        "label": "CURP",
        "entityType": "identity",
        "priority": 2
    },
    {
        "key": "ine",
        "label": "INE",
        "entityType": "identity",
        "priority": 3
    },
    {
        "key": "passport",
        "label": "Pasaporte",
        "entityType": "identity",
        "priority": 4
    },
    {
        "key": "_whatsapp_customer_id",
        "label": "WhatsApp Customer ID",
        "entityType": "identity",
        "priority": -1
    },
]
for data_model in data_models:
    try:
        altscore.borrower_central.data_models.create(data_model)
    except Exception as e:
        print(e)
        pass

# %%
borrower = altscore.borrower_central.borrowers.create({
    "label": "Nueva tienda",
    "persona": "individual"
})
# %%
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower,
        "key": "rfc",
        "value": "XAXX010101000"
    }
)
#%%
altscore.borrower_central.identities.create(
    {
        "borrowerId": borrower,
        "key": "rfc",
        "value": "YYYY010101000"
    },
    update_if_exists=True
)
# %%
