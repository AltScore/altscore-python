from uuid import uuid4
import datetime as dt

from fuzzywuzzy import process

from altscore.borrower_central.model.borrower import BorrowerSync, BorrowerAsync
from altscore.borrower_central.model.store_packages import altdata_source_slug
from altscore.altdata.model.data_request import SourceConfig
from altscore.macros.validate_inputs import validate_borrower_data
from typing import Optional, Tuple, List, Dict, Union
import asyncio
from loguru import logger


class MacrosSync:
    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def create_borrower(self, borrower_data: dict) -> Optional[BorrowerSync]:
        identities_to_create, borrower_fields_to_create = validate_borrower_data(borrower_data)
        borrower_id = self.altscore_client.borrower_central.borrowers.create(
            {
                "label": borrower_data.get("label"),
                "persona": borrower_data["persona"],
                "tags": borrower_data.get("tags", []),
                "flag": borrower_data.get("flag"),
                "riskRating": borrower_data.get("risk_rating") or borrower_data.get("riskRating"),
                "repaymentRiskRating": borrower_data.get("repayment_risk_rating") or \
                                       borrower_data.get("repaymentRiskRating"),
            }
        )
        try:
            for identity_key in identities_to_create:
                key = identity_key.split(".")[-1]
                value = borrower_data[identity_key]
                self.altscore_client.borrower_central.identities.create(
                    {
                        "borrower_id": borrower_id,
                        "key": key,
                        "value": value
                    }
                )
            for field_key in borrower_fields_to_create:
                key = field_key.split(".")[-1]
                value = borrower_data[field_key]
                self.altscore_client.borrower_central.borrower_fields.create(
                    {
                        "borrower_id": borrower_id,
                        "key": key,
                        "value": value
                    }
                )

            if len(borrower_data.get("points_of_contact", [])) > 0:
                for point_of_contact in borrower_data.get("points_of_contact"):
                    self.altscore_client.borrower_central.points_of_contact.create(
                        {
                            "borrower_id": borrower_id,
                            **point_of_contact
                        }
                    )

            if len(borrower_data.get("identities", [])) > 0:
                for identity in borrower_data["identities"]:
                    identity_id = self.altscore_client.borrower_central.identities.create(
                        {
                            "borrower_id": borrower_id,
                            **identity
                        }
                    )
                    if len(identity.get("attachments", [])) > 0:
                        identity_obj = self.altscore_client.borrower_central.identities.retieve(identity_id)
                        for attachment in identity["attachments"]:
                            identity_obj.post_attachment(attachment)

            if len(borrower_data.get("borrower_fields", [])) > 0:
                for borrower_field in borrower_data["borrower_fields"]:
                    self.altscore_client.borrower_central.borrower_fields.create(
                        {
                            "borrower_id": borrower_id,
                            **borrower_field
                        }
                    )

            if len(borrower_data.get("addresses", [])) > 0:
                for address in borrower_data["addresses"]:
                    address_id = self.altscore_client.borrower_central.addresses.create(
                        {
                            "borrower_id": borrower_id,
                            **address
                        }
                    )
                    if len(address.get("attachments", [])) > 0:
                        address_obj = self.altscore_client.borrower_central.addresses.retieve(address_id)
                        for attachment in address["attachments"]:
                            address_obj.post_attachment(attachment)

            if len(borrower_data.get("documents", [])) > 0:
                for document in borrower_data.get("documents"):
                    document_id = self.altscore_client.borrower_central.documents.create(
                        {
                            "borrower_id": borrower_id,
                            **document
                        }
                    )
                    if len(document.get("attachments", [])) > 0:
                        document_obj = self.altscore_client.borrower_central.documents.retieve(document_id)
                        for attachment in document["attachments"]:
                            document_obj.post_attachment(attachment)

            return self.altscore_client.borrower_central.borrowers.retrieve(borrower_id)
        except Exception as e:
            logger.error(f"Error creating borrower, deleting {borrower_id}")
            logger.exception(e)
            self.altscore_client.borrower_central.borrowers.delete(borrower_id)
            return None

    def new_cms_client_from_borrower(
            self, borrower_id: str,
            partner_id: str = None,
            legal_name_identity_key: Optional[str] = None,
            tax_id_identity_key: Optional[str] = None,
            external_id_identity_key: str = None,
            dba_identity_key: Optional[str] = None
    ) -> str:

        def find_identity_value_or_error(_borrower, identity_key):
            identity = _borrower.get_identity_by_key(key=identity_key)
            if identity is None:
                raise LookupError(f"Identity {identity_key} not found for borrower {borrower_id}")
            else:
                return identity.data.value

        borrower = self.altscore_client.borrower_central.borrowers.retrieve(borrower_id)
        if borrower is None:
            raise LookupError(f"Borrower {borrower_id} not found")

        if external_id_identity_key is not None:
            external_id = find_identity_value_or_error(borrower, external_id_identity_key)
        else:
            # carefull as the system validates unique external_id per partner per tenant
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
            # carefull as the system validates unique tax_id per partner per tenant
            tax_id = f"NA-{str(uuid4())[:8]}"

        address = borrower.get_main_address()
        if address is None:
            address = "N/A"
        else:
            address = address.data.get_address_str()

        email = borrower.get_main_point_of_contact(contact_method="email")
        if email is None:
            email = "na@na.com"
        else:
            email = email.data.value

        phone = borrower.get_main_point_of_contact(contact_method="phone")
        if phone is None:
            phone = "N/A"
        else:
            phone = phone.data.value

        client_data = {"externalId": external_id, "legalName": legal_name, "taxId": tax_id, "dba": dba,
                       "address": address, "emailAddress": email, "phoneNumber": phone, "partnerId": partner_id,
                       "borrowerId": borrower_id}

        # see if there is already a cms client with the given external id
        cms_client = self.altscore_client.cms.clients.retrieve_by_external_id(external_id=external_id)
        if cms_client is not None:
            # associate the borrower with the client
            borrower.associate_cms_client_id(cms_client.data.id)
            # update the client with the new legal name and tax id
            self.altscore_client.cms.clients.patch(
                resource_id=cms_client.data.id,
                patch_data={
                    "legalName": legal_name,
                    "taxId": tax_id,
                    "emailAddress": email,
                    "borrowerId": borrower_id
                }
            )
            return cms_client.data.id
        else:
            client_id = self.altscore_client.cms.clients.create(new_entity_data=client_data)
            borrower.associate_cms_client_id(client_id)
            return client_id

    def get_unique_borrower_field_values(self, field_key: str):
        field_values = self.altscore_client.borrower_central.borrower_fields.count_distinct_values(field_key)
        return [item["value"] for item in field_values]

    def evaluate_value_migration(self, target_values: list, current_values: list, threshold = 85):
        approved_changes, doubt = [], []
        for current in current_values:
            new_val = process.extractOne(current, target_values, score_cutoff=threshold)
            if new_val is not None and current != new_val[0]: # don't add if is the same value
                approved_changes.append((current, new_val[0]))
            elif new_val is None:
                doubt.append(current)

        return approved_changes, doubt

    def migrate_borrower_field_allowed_values(
            self,
            field_key: str,
            replace_values: List[Tuple[str, str]],
            allowed_values= None
    ):
        data_model = self.altscore_client.borrower_central.data_models.query(
            entity_type="borrower_field",
            key=field_key,
        )

        if data_model is None or data_model == []:
            raise Exception("No data model found with key {}".format(field_key))

        for value, target in replace_values:
            self.altscore_client.borrower_central.borrower_fields.bulk_update_field_values(field_key, value, target)

        if allowed_values is not None:
            self.altscore_client.borrower_central.data_models.patch(
                data_model[0].data.id,
                {
                    "allowedValues": allowed_values
                }
            )

    def enrich_borrower(
            self,
            borrower_id: str,
            sources: List[Dict],
            input_keys: Dict,
            data_age_minutes: int = 360,
            timeout_seconds: int = 120,
    ) -> dict:
        """
        Full AltData enrichment cycle with caching.

        Checks freshness for each source, calls AltData for stale/missing ones,
        stores results as packages. Returns a summary dict.

        Args:
            borrower_id: The borrower to enrich
            sources: List of source configs, e.g. [{"sourceId": "ECU-PUB-0002", "version": "v1"}]
            input_keys: Identity keys for AltData lookup, e.g. {"person_id": "123"}
            data_age_minutes: Max age in minutes before a package is considered stale (default 360)
            timeout_seconds: AltData sync call timeout (default 120)

        Returns:
            dict with keys: source_results, all_sources_ok, sources_created, sources_fresh, sources_failed
        """
        bc = self.altscore_client.borrower_central
        ad = self.altscore_client.altdata

        data_age = dt.timedelta(minutes=data_age_minutes)
        source_results = []
        sources_to_call = []

        for src in sources:
            s = SourceConfig.parse_obj(src) if isinstance(src, dict) else src
            slug = altdata_source_slug(s.source_id, s.version)
            pkg = bc.store_packages.retrieve_source_package(
                source_id=slug, borrower_id=borrower_id, data_age=data_age
            )
            if pkg is not None:
                source_results.append({
                    "source_slug": slug, "package_id": pkg.data.id, "status": "fresh"
                })
            else:
                sources_to_call.append(s)

        if sources_to_call:
            try:
                result = ad.requests.new_sync(
                    input_keys=input_keys,
                    sources_config=sources_to_call,
                    timeout=timeout_seconds,
                )
                for call in result.call_summary:
                    slug = altdata_source_slug(call.source_id, call.version)
                    if call.is_success:
                        pkg_id = bc.store_packages.create_from_altdata_request_result(
                            borrower_id=borrower_id,
                            source_id=call.source_id,
                            altdata_request_result=result,
                        )
                        source_results.append({
                            "source_slug": slug, "package_id": pkg_id, "status": "created"
                        })
                    else:
                        source_results.append({
                            "source_slug": slug, "status": "failed",
                            "error": call.error_message or "Unknown error"
                        })
            except Exception as e:
                for s in sources_to_call:
                    slug = altdata_source_slug(s.source_id, s.version)
                    if not any(r["source_slug"] == slug for r in source_results):
                        source_results.append({
                            "source_slug": slug, "status": "failed", "error": str(e)
                        })

        created = sum(1 for r in source_results if r["status"] == "created")
        fresh = sum(1 for r in source_results if r["status"] == "fresh")
        failed = sum(1 for r in source_results if r["status"] == "failed")

        return {
            "source_results": source_results,
            "all_sources_ok": failed == 0,
            "sources_created": created,
            "sources_fresh": fresh,
            "sources_failed": failed,
        }

class MacrosAsync:
    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    async def create_borrower(self, borrower_data: dict) -> Optional[BorrowerAsync]:
        identities_to_create, borrower_fields_to_create = validate_borrower_data(borrower_data)
        borrower_id = await self.altscore_client.borrower_central.borrowers.create(
            {
                "label": borrower_data.get("label"),
                "persona": borrower_data["persona"],
                "tags": borrower_data.get("tags", []),
                "flag": borrower_data.get("flag"),
                "riskRating": borrower_data.get("risk_rating") or borrower_data.get("riskRating"),
                "repaymentRiskRating": borrower_data.get("repayment_risk_rating") or \
                                       borrower_data.get("repaymentRiskRating"),
            }
        )
        try:
            calls = []
            for identity_key in identities_to_create:
                key = identity_key.split(".")[-1]
                value = borrower_data[identity_key]
                calls.append(self.altscore_client.borrower_central.identities.create(
                    {
                        "borrower_id": borrower_id,
                        "key": key,
                        "value": value
                    }
                ))
            for field_key in borrower_fields_to_create:
                key = field_key.split(".")[-1]
                value = borrower_data[field_key]
                calls.append(self.altscore_client.borrower_central.borrower_fields.create(
                    {
                        "borrower_id": borrower_id,
                        "key": key,
                        "value": value
                    }
                ))
            if len(borrower_data.get("points_of_contact", [])) > 0:
                for point_of_contact in borrower_data.get("points_of_contact"):
                    calls.append(self.altscore_client.borrower_central.points_of_contact.create(
                        {
                            "borrower_id": borrower_id,
                            **point_of_contact
                        }
                    ))
            await asyncio.gather(*calls)

            # if this entities have attachments we cannot make them concurrently
            if len(borrower_data.get("identities", [])) > 0:
                for identity in borrower_data["identities"]:
                    identity_id = await self.altscore_client.borrower_central.identities.create(
                        {
                            "borrower_id": borrower_id,
                            **identity
                        }
                    )
                    if len(identity.get("attachments", [])) > 0:
                        identity_obj = await self.altscore_client.borrower_central.identities.retieve(identity_id)
                        for attachment in identity["attachments"]:
                            await identity_obj.post_attachment(attachment)

            if len(borrower_data.get("borrower_fields", [])) > 0:
                for borrower_field in borrower_data["borrower_fields"]:
                    await self.altscore_client.borrower_central.borrower_fields.create(
                        {
                            "borrower_id": borrower_id,
                            **borrower_field
                        }
                    )

            if len(borrower_data.get("addresses", [])) > 0:
                for address in borrower_data["addresses"]:
                    address_id = await self.altscore_client.borrower_central.addresses.create(
                        {
                            "borrower_id": borrower_id,
                            **address
                        }
                    )
                    if len(address.get("attachments", [])) > 0:
                        address_obj = await self.altscore_client.borrower_central.addresses.retieve(address_id)
                        for attachment in address["attachments"]:
                            await address_obj.post_attachment(attachment)

            if len(borrower_data.get("documents", [])) > 0:
                for document in borrower_data.get("documents"):
                    document_id = await self.altscore_client.borrower_central.documents.create(
                        {
                            "borrower_id": borrower_id,
                            **document
                        }
                    )
                    if len(document.get("attachments", [])) > 0:
                        document_obj = await self.altscore_client.borrower_central.documents.retieve(document_id)
                        for attachment in document["attachments"]:
                            await document_obj.post_attachment(attachment)

            return await self.altscore_client.borrower_central.borrowers.retrieve(borrower_id)
        except Exception as e:
            logger.error(f"Error creating borrower, deleting {borrower_id}")
            logger.exception(e)
            await self.altscore_client.borrower_central.borrowers.delete(borrower_id)
            return None

    async def new_cms_client_from_borrower(
            self, borrower_id: str, partner_id: str, legal_name_identity_key: str, tax_id_identity_key: str,
            external_id_identity_key: str = None, dba_identity_key: Optional[str] = None
    ) -> str:
        async def find_identity_value_or_error(_borrower, identity_key):
            identity = await _borrower.get_identity_by_key(key=identity_key)
            if identity is None:
                raise LookupError(f"Identity {identity_key} not found for borrower {borrower_id}")
            else:
                return identity.data.value

        borrower = await self.altscore_client.borrower_central.borrowers.retrieve(borrower_id)
        if borrower is None:
            raise LookupError(f"Borrower {borrower_id} not found")

        if external_id_identity_key is not None:
            external_id = await find_identity_value_or_error(borrower, external_id_identity_key)
        else:
            # carefull as the system validates unique external_id per partner per tenant
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
            # carefull as the system validates unique tax_id per partner per tenant
            tax_id = f"NA-{str(uuid4())[:8]}"

        address = await borrower.get_main_address()
        if address is None:
            address = "N/A"
        else:
            address = address.data.get_address_str()

        email = await borrower.get_main_point_of_contact(contact_method="email")
        if email is None:
            email = "na@na.com"
        else:
            email = email.data.value

        phone = await borrower.get_main_point_of_contact(contact_method="phone")
        if phone is None:
            phone = "N/A"
        else:
            phone = phone.data.value

        client_data = {"externalId": external_id, "legalName": legal_name, "taxId": tax_id, "dba": dba,
                       "address": address, "emailAddress": email, "phoneNumber": phone, "partnerId": partner_id,
                       "borrowerId": borrower_id}
        # see if there is already a cms client with the given external id
        cms_client = await self.altscore_client.cms.clients.retrieve_by_external_id(external_id=external_id)
        if cms_client is not None:
            # associate the borrower with the client
            await borrower.associate_cms_client_id(cms_client.data.id)
            # update the client with the new legal name and tax id
            await self.altscore_client.cms.clients.patch(
                resource_id=cms_client.data.id,
                patch_data={
                    "legalName": legal_name,
                    "taxId": tax_id,
                    "emailAddress": email,
                    "borrowerId": borrower_id
                }
            )
            return cms_client.data.id
        else:
            client_id = await self.altscore_client.cms.clients.create(new_entity_data=client_data)
            await borrower.associate_cms_client_id(client_id)
            return client_id

    async def get_unique_borrower_field_values(self, field_key: str):
        field_values = await self.altscore_client.borrower_central.borrower_fields.count_distinct_values(field_key)
        return [item["value"] for item in field_values]

    async def evaluate_value_migration(self, target_values: list, current_values: list, threshold = 85):
        approved_changes, doubt = [], []
        for current in current_values:
            new_val = process.extractOne(current, target_values, score_cutoff=threshold)
            if new_val is not None and current != new_val[0]: # don't add if is the same value
                approved_changes.append((current, new_val[0]))
            elif new_val is None:
                doubt.append(current)

        return approved_changes, doubt

    async def migrate_borrower_field_allowed_values(
            self,
            field_key: str,
            replace_values: List[Tuple[str, str]],
            new_allowed_values: List[str]
    ):
        replacing_values = [val[1] for val in replace_values]
        if not set(replacing_values).issubset(set(new_allowed_values)):
            raise ValueError("Trying to set values not present in the new allowed values")

        data_model = await self.altscore_client.borrower_central.data_models.query(
            entity_type="borrower_field",
            key=field_key,
        )

        if data_model is None or data_model == []:
            raise Exception("No data model found with key {}".format(field_key))

        async_calls = []

        for value, target in replace_values:
            call = asyncio.create_task(self.altscore_client.borrower_central.borrower_fields.bulk_update_field_values(
                field_key, value, target
            ))
            async_calls.append(call)

        await asyncio.gather(*async_calls)

        await self.altscore_client.borrower_central.data_models.patch(
            data_model[0].data.id,
            {
                "allowedValues": new_allowed_values
            }
        )

    async def enrich_borrower(
            self,
            borrower_id: str,
            sources: List[Dict],
            input_keys: Dict,
            data_age_minutes: int = 360,
            timeout_seconds: int = 120,
    ) -> dict:
        """
        Full AltData enrichment cycle with caching.

        Checks freshness for each source, calls AltData for stale/missing ones,
        stores results as packages. Returns a summary dict.

        Args:
            borrower_id: The borrower to enrich
            sources: List of source configs, e.g. [{"sourceId": "ECU-PUB-0002", "version": "v1"}]
            input_keys: Identity keys for AltData lookup, e.g. {"person_id": "123"}
            data_age_minutes: Max age in minutes before a package is considered stale (default 360)
            timeout_seconds: AltData sync call timeout (default 120)

        Returns:
            dict with keys: source_results, all_sources_ok, sources_created, sources_fresh, sources_failed
        """
        bc = self.altscore_client.borrower_central
        ad = self.altscore_client.altdata

        data_age = dt.timedelta(minutes=data_age_minutes)
        source_results = []
        sources_to_call = []

        for src in sources:
            s = SourceConfig.parse_obj(src) if isinstance(src, dict) else src
            slug = altdata_source_slug(s.source_id, s.version)
            pkg = await bc.store_packages.retrieve_source_package(
                source_id=slug, borrower_id=borrower_id, data_age=data_age
            )
            if pkg is not None:
                source_results.append({
                    "source_slug": slug, "package_id": pkg.data.id, "status": "fresh"
                })
            else:
                sources_to_call.append(s)

        if sources_to_call:
            try:
                result = await ad.requests.new_sync(
                    input_keys=input_keys,
                    sources_config=sources_to_call,
                    timeout=timeout_seconds,
                )
                for call in result.call_summary:
                    slug = altdata_source_slug(call.source_id, call.version)
                    if call.is_success:
                        pkg_id = await bc.store_packages.create_from_altdata_request_result(
                            borrower_id=borrower_id,
                            source_id=call.source_id,
                            altdata_request_result=result,
                        )
                        source_results.append({
                            "source_slug": slug, "package_id": pkg_id, "status": "created"
                        })
                    else:
                        source_results.append({
                            "source_slug": slug, "status": "failed",
                            "error": call.error_message or "Unknown error"
                        })
            except Exception as e:
                for s in sources_to_call:
                    slug = altdata_source_slug(s.source_id, s.version)
                    if not any(r["source_slug"] == slug for r in source_results):
                        source_results.append({
                            "source_slug": slug, "status": "failed", "error": str(e)
                        })

        created = sum(1 for r in source_results if r["status"] == "created")
        fresh = sum(1 for r in source_results if r["status"] == "fresh")
        failed = sum(1 for r in source_results if r["status"] == "failed")

        return {
            "source_results": source_results,
            "all_sources_ok": failed == 0,
            "sources_created": created,
            "sources_fresh": fresh,
            "sources_failed": failed,
        }
