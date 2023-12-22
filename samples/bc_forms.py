from altscore import AltScore, borrower_sign_up_with_form
from decouple import config

# %%
altscore, borrower_id = borrower_sign_up_with_form(
    persona="individual",
    template_slug="whatsapp-landbot",
    tenant="arca",
    environment="staging"
)

# %%

