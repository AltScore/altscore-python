from altscore.cms.model.partners import PartnersSyncModule, PartnersAsyncModule
from altscore.cms.model.clients import ClientsSyncModule, ClientsAsyncModule
from altscore.cms.helpers import build_headers


class CMSSync:

    def __init__(self, altscore_client):
        self.clients = ClientsSyncModule(altscore_client)
        self.partners = PartnersSyncModule(altscore_client)


class CMSAsync:

    def __init__(self, altscore_client):
        self.clients = ClientsAsyncModule(altscore_client)
        self.partners = PartnersAsyncModule(altscore_client)
