from typing import List
import json
from pydantic import BaseModel


class Configuration(BaseModel):
    tenant: str
    environment: str
    api_key: str


class AltScoreConfiguration(BaseModel):
    configurations: List[Configuration]


class Session:
    def __init__(self, tenant="default", secret_path="~/.altscore", environment="production"):
        self.secret_path = secret_path
        self.tenant = tenant
        self.configuration = load_secrets(tenant=tenant, environment=environment, file_path=secret_path)
        self.api_key = self.configuration.api_key

    def new(self, tenant=None):
        if tenant is None:
            tenant = self.tenant
        return Session(tenant=tenant, secret_path=self.secret_path)


def load_secrets(tenant, environment, file_path):
    with open(file_path, "r") as f:
        secrets = AltScoreConfiguration.model_validate(json.load(f))
    for config in secrets.configurations:
        if config.environment != environment:
            continue
        if tenant == "default":
            return config
        if config.tenant == tenant:
            return config
    raise ValueError("Tenant not found, or empty configuration")
