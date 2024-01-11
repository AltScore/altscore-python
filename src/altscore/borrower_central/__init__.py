from altscore.borrower_central.model.borrower import BorrowersAsyncModule, BorrowersSyncModule
from altscore.borrower_central.model.data_models import DataModelAsyncModule, DataModelSyncModule
from altscore.borrower_central.model.executions import ExecutionAsyncModule, ExecutionSyncModule
from altscore.borrower_central.model.tools import ReportGeneratorAsyncModule, ReportGeneratorSyncModule
from altscore.borrower_central.model.form_templates import FormTemplatesAsyncModule, FormTemplatesSyncModule
from altscore.borrower_central.model.otp_templates import OTPTemplatesAsyncModule, OTPTemplatesSyncModule
from altscore.borrower_central.model.addresses import AddressesAsyncModule, AddressesSyncModule
from altscore.borrower_central.model.authorizations import AuthorizationsAsyncModule, AuthorizationsSyncModule
from altscore.borrower_central.model.borrower_fields import BorrowerFieldsAsyncModule, BorrowerFieldsSyncModule
from altscore.borrower_central.model.documents import DocumentsAsyncModule, DocumentsSyncModule
from altscore.borrower_central.model.identities import IdentitiesAsyncModule, IdentitiesSyncModule
from altscore.borrower_central.model.points_of_contact import PointOfContactAsyncModule, PointOfContactSyncModule
from altscore.borrower_central.model.relationships import RelationshipsAsyncModule, RelationshipsSyncModule
from altscore.borrower_central.model.store_packages import PackagesAsyncModule, PackagesSyncModule
from altscore.borrower_central.model.store_sources import SourcesAsyncModule, SourcesSyncModule
from altscore.borrower_central.model.workflows import WorkflowsAsyncModule, WorkflowsSyncModule
from altscore.borrower_central.model.evaluators import EvaluatorAsyncModule, EvaluatorSyncModule
from altscore.borrower_central.model.forms import FormsAsyncModule, FormsSyncModule
from altscore.borrower_central.model.policy_alerts import AlertsAsyncModule, AlertsSyncModule
from altscore.borrower_central.model.policy_rules import RulesAsyncModule, RulesSyncModule
from altscore.borrower_central.model.integrations.sat import SatIntegrationAsyncModule, SatIntegrationSyncModule


class BorrowerCentralAsync:

    def __init__(self, altscore_client):
        self.addresses = AddressesAsyncModule(altscore_client)
        self.authorizations = AuthorizationsAsyncModule(altscore_client)
        self.borrowers = BorrowersAsyncModule(altscore_client)
        self.borrower_fields = BorrowerFieldsAsyncModule(altscore_client)
        self.data_models = DataModelAsyncModule(altscore_client)
        self.documents = DocumentsAsyncModule(altscore_client)
        self.executions = ExecutionAsyncModule(altscore_client)
        self.identities = IdentitiesAsyncModule(altscore_client)
        self.workflows = WorkflowsAsyncModule(altscore_client)
        self.points_of_contact = PointOfContactAsyncModule(altscore_client)
        self.relationships = RelationshipsAsyncModule(altscore_client)
        self.report_generator = ReportGeneratorAsyncModule(altscore_client)
        self.form_templates = FormTemplatesAsyncModule(altscore_client)
        self.otp_templates = OTPTemplatesAsyncModule(altscore_client)
        self.store_packages = PackagesAsyncModule(altscore_client)
        self.store_sources = SourcesAsyncModule(altscore_client)
        self.evaluators = EvaluatorAsyncModule(altscore_client)
        self.forms = FormsAsyncModule(altscore_client)
        self.alerts = AlertsAsyncModule(altscore_client)
        self.rules = RulesAsyncModule(altscore_client)
        self.sat_integration = SatIntegrationAsyncModule(altscore_client)


class BorrowerCentralSync:

    def __init__(self, altscore_client):
        self.addresses = AddressesSyncModule(altscore_client)
        self.authorizations = AuthorizationsSyncModule(altscore_client)
        self.borrowers = BorrowersSyncModule(altscore_client)
        self.borrower_fields = BorrowerFieldsSyncModule(altscore_client)
        self.data_models = DataModelSyncModule(altscore_client)
        self.documents = DocumentsSyncModule(altscore_client)
        self.executions = ExecutionSyncModule(altscore_client)
        self.workflows = WorkflowsSyncModule(altscore_client)
        self.identities = IdentitiesSyncModule(altscore_client)
        self.points_of_contact = PointOfContactSyncModule(altscore_client)
        self.relationships = RelationshipsSyncModule(altscore_client)
        self.report_generator = ReportGeneratorSyncModule(altscore_client)
        self.form_templates = FormTemplatesSyncModule(altscore_client)
        self.otp_templates = OTPTemplatesSyncModule(altscore_client)
        self.store_packages = PackagesSyncModule(altscore_client)
        self.store_sources = SourcesSyncModule(altscore_client)
        self.evaluators = EvaluatorSyncModule(altscore_client)
        self.forms = FormsSyncModule(altscore_client)
        self.alerts = AlertsSyncModule(altscore_client)
        self.rules = RulesSyncModule(altscore_client)
        self.sat_integration = SatIntegrationSyncModule(altscore_client)
