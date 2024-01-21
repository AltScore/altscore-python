import asyncio

from altscore.borrower_central import BorrowerCentralAsync, BorrowerCentralSync
from altscore.altdata import AltDataSync, AltDataAsync
from altscore.cms import CMSSync, CMSAsync
from typing import Optional, Union
import warnings

warnings.filterwarnings("ignore")


class AltScoreBase:
    _altdata_base_url = "https://data.altscore.ai"

    def __init__(self, api_key: str = None, tenant: str = "default",
                 environment: str = "production", user_token: Optional[str] = None,
                 form_token: Optional[str] = None, partner_id: Optional[str] = None):
        self.environment = environment
        self.api_key = api_key
        self.user_token = user_token
        self.tenant = tenant
        self.form_token = form_token
        self._partner_id = partner_id

    def __repr__(self):
        return f"AltScore({self.tenant}, {self.environment})"

    @property
    def _borrower_central_base_url(self):
        if self.environment == "production":
            return "https://bc.altscore.ai"
        elif self.environment == "staging":
            return "https://borrower-central-staging-zosvdgvuuq-uc.a.run.app"
        elif self.environment == "sandbox":
            return "https://bc.sandbox.altscore.ai"
        elif self.environment == "local":
            return "http://localhost:8888"
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
        elif self.environment == "local":
            return "http://localhost:8889"
        else:
            raise ValueError(f"Unknown environment: {self.environment}")


class AltScore(AltScoreBase):
    _async_mode = False

    def __init__(self, api_key: str = None, tenant: str = "default",
                 environment: str = "production", user_token: Optional[str] = None,
                 form_token: Optional[str] = None, partner_id: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            tenant=tenant,
            environment=environment,
            user_token=user_token,
            form_token=form_token,
            partner_id=partner_id)
        self.borrower_central = BorrowerCentralSync(self)
        self.altdata = AltDataSync(self)
        self.cms = CMSSync(self)

    @property
    def partner_id(self) -> Optional[str]:
        if self._partner_id is None:
            partner_id = self.cms.partners.me().data.partner_id
            self._partner_id = partner_id
        return self._partner_id

    def new_cms_client_from_borrower(
            self, borrower_id: str,
            legal_name_identity_key: Optional[str] = None,
            tax_id_identity_key: Optional[str] = None,
            external_id_identity_key: str = None,
            dba_identity_key: Optional[str] = None,
            partner_id: Optional[str] = None
    ) -> str:

        def find_identity_value_or_error(_borrower, identity_key):
            identity = _borrower.get_identity_by_key(key=identity_key)
            if identity is None:
                raise LookupError(f"Identity {identity_key} not found for borrower {borrower_id}")
            else:
                return identity.data.value

        borrower = self.borrower_central.borrowers.retrieve(borrower_id)
        if borrower is None:
            raise LookupError(f"Borrower {borrower_id} not found")

        if external_id_identity_key is not None:
            external_id = find_identity_value_or_error(borrower, external_id_identity_key)
        else:
            external_id = borrower_id

        if legal_name_identity_key is not None:
            legal_name = find_identity_value_or_error(borrower, legal_name_identity_key)
        else:
            legal_name = "N/A"

        if borrower.data.persona == "business":
            if dba_identity_key is not None:
                dba = find_identity_value_or_error(borrower, dba_identity_key)
            else:
                dba = legal_name
        else:
            dba = "N/A"

        if tax_id_identity_key is not None:
            tax_id = find_identity_value_or_error(borrower, tax_id_identity_key)
        else:
            tax_id = "N/A"

        address = borrower.get_main_address()
        if address is None:
            address = "N/A"
        else:
            address = address.data.get_address_str()

        email = borrower.get_main_point_of_contact(contact_method="email")
        if email is None:
            email = "N/A"
        else:
            email = email.data.value

        phone = borrower.get_main_point_of_contact(contact_method="phone")
        if phone is None:
            phone = "N/A"
        else:
            phone = phone.data.value

        client_data = {
            "externalId": external_id,
            "legalName": legal_name,
            "taxId": tax_id,
            "dba": dba,
            "address": address,
            "emailAddress": email,
            "phoneNumber": phone
        }
        if partner_id is not None:
            client_data["partnerId"] = partner_id

        client_id = self.cms.clients.create(new_entity_data=client_data)
        borrower.associate_cms_client_id(client_id)
        return client_id


class AltScoreAsync(AltScoreBase):
    _async_mode = True

    def __init__(self, api_key: str = None, tenant: str = "default",
                 environment: str = "production", user_token: Optional[str] = None,
                 form_token: Optional[str] = None, partner_id: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            tenant=tenant,
            environment=environment,
            user_token=user_token,
            form_token=form_token,
            partner_id=partner_id)
        self.borrower_central = BorrowerCentralAsync(self)
        self.altdata = AltDataAsync(self)
        self.cms = CMSAsync(self)

    @property
    def partner_id(self) -> Optional[str]:
        if self._partner_id is None:
            partner = asyncio.run(self.cms.partners.me())
            partner_id = partner.data.partner_id
            self._partner_id = partner_id
        return self._partner_id

    async def new_cms_client_from_borrower(
            self, borrower_id: str, legal_name_identity_key: str, tax_id_identity_key: str,
            external_id_identity_key: str = None, dba_identity_key: Optional[str] = None,
            partner_id: Optional[str] = None
    ) -> str:
        async def find_identity_value_or_error(_borrower, identity_key):
            identity = await _borrower.get_identity_by_key(key=identity_key)
            if identity is None:
                raise LookupError(f"Identity {identity_key} not found for borrower {borrower_id}")
            else:
                return identity.data.value

        borrower = await self.borrower_central.borrowers.retrieve(borrower_id)
        if borrower is None:
            raise LookupError(f"Borrower {borrower_id} not found")

        if external_id_identity_key is not None:
            external_id = await find_identity_value_or_error(borrower, external_id_identity_key)
        else:
            external_id = borrower_id

        if legal_name_identity_key is not None:
            legal_name = await find_identity_value_or_error(borrower, legal_name_identity_key)
        else:
            legal_name = "N/A"

        if borrower.data.persona == "business":
            if dba_identity_key is not None:
                dba = await find_identity_value_or_error(borrower, dba_identity_key)
            else:
                dba = legal_name
        else:
            dba = "N/A"

        if tax_id_identity_key is not None:
            tax_id = await find_identity_value_or_error(borrower, tax_id_identity_key)
        else:
            tax_id = "N/A"

        address = await borrower.get_main_address()
        if address is None:
            address = "N/A"
        else:
            address = address.data.get_address_str()

        email = await borrower.get_main_point_of_contact(contact_method="email")
        if email is None:
            email = "N/A"
        else:
            email = email.data.value

        phone = await borrower.get_main_point_of_contact(contact_method="phone")
        if phone is None:
            phone = "N/A"
        else:
            phone = phone.data.value

        client_data = {
            "externalId": external_id,
            "legalName": legal_name,
            "taxId": tax_id,
            "dba": dba,
            "address": address,
            "emailAddress": email,
            "phoneNumber": phone
        }
        if partner_id is not None:
            client_data["partnerId"] = partner_id

        client_id = await self.cms.clients.create(new_entity_data=client_data)
        await borrower.associate_cms_client_id(client_id)
        return client_id


def borrower_sign_up_with_form(
        persona: str,
        template_slug: str,
        tenant: str,
        environment: str = "production",
        async_mode: bool = False
) -> (Union[AltScore, AltScoreAsync], str, str, str):
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
    if async_mode:
        altscore_module = AltScoreAsync(
            form_token=new_borrower.form_token,
            tenant=tenant,
            environment=environment,
        )
    else:
        altscore_module = AltScore(
            form_token=new_borrower.form_token,
            tenant=tenant,
            environment=environment,
        )
    return altscore_module, new_borrower.borrower_id, form_id
