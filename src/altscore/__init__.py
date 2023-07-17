from altscore.borrower_central import BorrowerCentralAsync, BorrowerCentralSync
from altscore.altdata import AltdataSync
import warnings


class AltScore:
    _altdata_base_url = "https://data.altscore.ai"

    def __init__(self, api_key=None, tenant="default", async_mode=False, environment="production"):
        warnings.filterwarnings("ignore")
        self.environment = environment
        self.api_key = api_key
        self.tenant = tenant
        if async_mode:
            self.borrower_central = BorrowerCentralAsync(self)
            self.altdata = None
        else:
            self.borrower_central = BorrowerCentralSync(self)
            self.altdata = AltdataSync(self)

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
