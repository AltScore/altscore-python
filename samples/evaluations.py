from altscore import AltScore
from decouple import config

altscore = AltScore(api_key=config("ALTSCORE_API_KEY"), environment="staging")

#%%
eval_result = altscore.borrower_central.evaluators.evaluate(
    evaluator_input={
        "instance": {
            "referenceId": "430850",
            "referenceDate": "2023-06-22 07:53:04",
            "data": {
                "variable-1": 0.75,
                "variable-3": "B",
                "variable-4": "E",
                "root_variable_1": "D",
                "root_variable_2": "E",
                "auto_approve": 0
            }
        },
        "entities": [
            {
                "entityId": "1",
                "role": "debtor",
                "data": {
                    "sub-variable": 2,
                    "dt-variable-2": 251
                }
            },
            {
                "entityId": "2",
                "role": "co-debtor",
                "data": {
                    "sub-variable": 15,
                    "dt-variable-2": 500
                }
            },
            {
                "entityId": "1",
                "role": "guarantor",
                "data": {
                    "sub-variable": 5,
                    "dt-variable-2": 500
                }
            }
        ]
    },
    evaluator_id="c2973fba-8da3-4bb4-b09f-f5d6799e1374"
)
#%%




