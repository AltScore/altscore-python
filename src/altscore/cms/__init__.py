from altscore.cms.model.partners import PartnersSyncModule, PartnersAsyncModule
from altscore.cms.model.clients import ClientsSyncModule, ClientsAsyncModule
from altscore.cms.model.dpas import DPAFlowsAsyncModule, DPAFlowsSyncModule
from altscore.cms.model.debts import DebtsAsyncModule, DebtsSyncModule
from altscore.cms.helpers import build_headers


class CMSSync:

    def __init__(self, altscore_client):
        self.clients = ClientsSyncModule(altscore_client)
        self.partners = PartnersSyncModule(altscore_client)
        self.dpas = DPAFlowsSyncModule(altscore_client)
        self.debts = DebtsSyncModule(altscore_client)


class CMSAsync:

    def __init__(self, altscore_client):
        self.clients = ClientsAsyncModule(altscore_client)
        self.partners = PartnersAsyncModule(altscore_client)
        self.dpas = DPAFlowsAsyncModule(altscore_client)
        self.debts = DebtsAsyncModule(altscore_client)
