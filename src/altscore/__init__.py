from altscore.borrower_central import BorrowerCentralAsync, BorrowerCentralSync
from altscore.altdata import AltdataSync
import warnings


class AltScore:
    _altdata_base_url = "https://data.altscore.ai"

    def __init__(self, api_key: str = None, tenant: str = "default", async_mode: bool = False,
                 environment: str = "production",
                 form_token: str = None):
        warnings.filterwarnings("ignore")
        self.environment = environment
        self.api_key = api_key
        self.tenant = tenant
        self.form_token = form_token
        if async_mode:
            self.borrower_central = BorrowerCentralAsync(self)
            self.altdata = None
        else:
            self.borrower_central = BorrowerCentralSync(self)
            self.altdata = AltdataSync(self)

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
