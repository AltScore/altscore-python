from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)

#%%
data_models = altscore.borrower_central.data_models.retrieve_all()
#%%
# List borrowers
borrowers = altscore.borrower_central.borrowers.query()
# List borrowers summary
borrowers_summary = altscore.borrower_central.borrowers.query_summary()
#%%
# Create a borrower
altscore.borrower_central.borrowers.create(
    {
        "label": "Juan Perez 2",
        "persona": "individual"
    }
)
#%%
# Create a borrower with macro
borrower = altscore.macros.create_borrower(
    {
        "label": "Juan Perez 3",
        "persona": "individual",
        "identity.person_id": "1234567890",
        "identity.full_name": "Juan Perez",
        "points_of_contact": [
            {
                "contactMethod": "email",
                "value": "sample@sample.com"
            },
            {
                "contactMethod": "phone",
                "value": "1234567890"
            }
        ],
        "addresses": [
            {
                "street1": "Av. Paseo de la Reforma 123",
                "neighborhood": "Juarez",
                "city": "Ciudad de Mexico",
                "state": "CDMX",
                "zipCode": "06600",
                "country": "MEX"
            }
        ]
    }
)
#%%
borrower = borrowers[0]