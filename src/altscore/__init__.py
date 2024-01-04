import asyncio

from altscore.borrower_central import BorrowerCentralAsync, BorrowerCentralSync
from altscore.altdata import AltdataSync
from altscore.cms import CMSSync, CMSAsync
from typing import Optional
import warnings

warnings.filterwarnings("ignore")


class AltScore:
    _altdata_base_url = "https://data.altscore.ai"

    def __init__(self, api_key: str = None, tenant: str = "default", async_mode: bool = False,
                 environment: str = "production", user_token: Optional[str] = None,
                 form_token: Optional[str] = None):
        self.environment = environment
        self.api_key = api_key
        self.user_token = user_token
        self.tenant = tenant
        self.form_token = form_token
        self._partner_id = None
        self._async_mode = async_mode
        if async_mode:
            self.borrower_central = BorrowerCentralAsync(self)
            self.altdata = None
            self.cms = CMSAsync(self)
        else:
            self.borrower_central = BorrowerCentralSync(self)
            self.altdata = AltdataSync(self)
            self.cms = CMSSync(self)

    def __repr__(self):
        return f"AltScore({self.tenant}, {self.environment})"

    @property
    def _borrower_central_base_url(self):
        if self.environment == "production":
            return "https://borrower-central-zosvdgvuuq-uc.a.run.app"
        elif self.environment == "staging":
            return "https://borrower-central-staging-zosvdgvuuq-uc.a.run.app"
        elif self.environment == "sandbox":
            return "https://borrower-central-sandbox-zosvdgvuuq-uc.a.run.app"
        else:
            raise ValueError(f"Unknown environment: {self.environment}")

    @property
    def _cms_base_url(self):
        if self.environment == "production":
            return "https://api.altscore.ai"
        elif self.environment == "staging":
            return "https://api.stg.altscore.ai"
        elif self.environment == "sandbox":
            return "https://api.sandbox.altscore.ai"
        else:
            raise ValueError(f"Unknown environment: {self.environment}")

    @property
    def partner_id(self) -> Optional[str]:
        if self._partner_id is None:
            if self._async_mode:
                partner_id = asyncio.run(self.cms.partners.me().data.partner_id)
            else:
                partner_id = self.cms.partners.me().data.partner_id
            self._partner_id = partner_id
        return self._partner_id


def borrower_sign_up_with_form(
        persona: str,
        template_slug: str,
        tenant: str,
        environment: str = "production",
        async_mode: bool = False
) -> (AltScore, str, str, str):
    client = AltScore(tenant=tenant, environment=environment)
    form_id = client.borrower_central.forms.create({
        "templateSlug": template_slug,
        "tenant": tenant
    })
    new_borrower = client.borrower_central.forms.command_borrower_sign_up(
        {
            "formId": form_id,
            "tenant": tenant,
            "persona": persona
        }
    )
    altscore_module = AltScore(
        form_token=new_borrower.form_token,
        tenant=tenant,
        environment=environment,
        async_mode=async_mode
    )
    return altscore_module, new_borrower.borrower_id, form_id
