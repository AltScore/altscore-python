from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)

steps_models = [
    {
        "order": -1,
        "label": "Rechazado",
        "key": "rejected",
        "entityType": "step"
    },
    {
        "order": 1,
        "label": "Nuevo",
        "key": "new",
        "entityType": "step"
    },
    {
        "order": 2,
        "label": "Pre-aprobado",
        "key": "pre_approved",
        "entityType": "step"
    },
    {
        "order": 3,
        "label": "Alta completada",
        "key": "onboarded",
        "entityType": "step"
    },
    {
        "order": 4,
        "label": "Aprobado",
        "key": "approved",
        "entityType": "step"
    },
    {
        "order": 5,
        "label": "Entregado",
        "key": "activated",
        "entityType": "step"
    },
    {
        "order": 6,
        "label": "Activo",
        "key": "active",
        "entityType": "step"
    }
]
for data_model in steps_models:
    try:
        altscore.borrower_central.data_models.create(data_model)
    except Exception as e:
        print(e)
        pass

#%%
borrowers = altscore.borrower_central.borrowers.query()
borrowers[0].set_current_step("active")
#%%
borrowers[0].get_current_step().data.model_dump()
#%%