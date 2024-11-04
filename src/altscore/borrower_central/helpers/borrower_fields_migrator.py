from typing import List

from altscore.borrower_central import BorrowerFieldsSyncModule, DataModelSyncModule, BorrowerFieldsAsyncModule
from fuzzywuzzy import process

from altscore.borrower_central.model.data_models import DataModelUpdate


class BorrowerFieldsMigrator:
    def __init__(self, altscore_client):
        self.altscore_client = altscore_client
        # init needed model modules (borrower_fields and data_model)
        self.borrower_field_module = BorrowerFieldsSyncModule(altscore_client=self.altscore_client)
        self.borrower_field_async_module = BorrowerFieldsAsyncModule(altscore_client=self.altscore_client)
        self.data_model_module = DataModelSyncModule(altscore_client=self.altscore_client)

    '''
    Receive a field key and obtain all the unique values of that field
    '''
    def get_unique_values(self, field_key: str) -> list:
        # query for the borrower field of given key
        field_values = self.borrower_field_module.query(
            data_type='borrower_field',
            key=field_key
        )
        # we might even suggest outliers if needed
        unique_values = set([item.data.value for item in field_values])
        return list(unique_values)

    '''
    Receive the field key, the new allowed values and an optional threshold
    
    '''
    def migrate_borrower_field_allowed_values(
            self,
            field_key: str,
            allowed_values: list,
            threshold = 0.85
    ):
        data_model = self.data_model_module.query(
            key=field_key,
        )

        if data_model is None or data_model == []:
            raise Exception('No data model found with key {}'.format(field_key))

        borrower_fields = self.borrower_field_module.query(
            data_type='borrower_field',
            key=field_key
        )
        borrower_fields = [item.data for item in borrower_fields]

        for bf in borrower_fields:
            new_val = process.extractOne(bf.value, allowed_values, score_cutoff=threshold)
            if new_val is not None:
                bf.value = new_val[0]
            # todo: think a way to treat values below the threshold
            # idea: return values that couldn't be updated
            # idea 2: change values to a default (?)

        for bf in borrower_fields:
            self.borrower_field_module.patch(bf.id, {"borrowerId": bf.id, "value": bf.value})

        self.data_model_module.patch(data_model[0].data.id,
        {
            "allowedValues": allowed_values,
        })
