from altscore.webhooks.model.webhooks import WebhookSyncModule, WebhookAsyncModule


class WebhookSync:
    def __init__(self, altscore_client):
        self.WebhookSync = WebhookSyncModule(altscore_client)

class WebhookAsync:
    def __init__(self, altscore_client):
        self.WebhookAsync = WebhookAsyncModule(altscore_client)
