from altscore.altdata.model.batch import BatchSyncModule
from altscore.altdata.model.data_request import RequestSyncModule


class AltdataSync:

    def __init__(self, altscore_client):
        self.batches = BatchSyncModule(altscore_client)
        self.requests = RequestSyncModule(altscore_client)
