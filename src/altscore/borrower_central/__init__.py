from altscore.borrower_central.model.borrower import BorrowersAsyncModule, BorrowersSyncModule
from altscore.borrower_central.model.data_models import DataModelAsyncModule, DataModelSyncModule
from altscore.borrower_central.model.executions import ExecutionAsyncModule, ExecutionSyncModule
from altscore.borrower_central.model.tools import ReportGeneratorAsyncModule, ReportGeneratorSyncModule, \
    CommunicationsAsyncModule, CommunicationsSyncModule
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
from altscore.borrower_central.model.store_secrets import SecretsAsyncModule, SecretsSyncModule
from altscore.borrower_central.model.workflows import WorkflowsAsyncModule, WorkflowsSyncModule
from altscore.borrower_central.model.evaluators import EvaluatorAsyncModule, EvaluatorSyncModule
from altscore.borrower_central.model.forms import FormsAsyncModule, FormsSyncModule
from altscore.borrower_central.model.policy_alerts import AlertsAsyncModule, AlertsSyncModule
from altscore.borrower_central.model.policy_rules import RulesAsyncModule, RulesSyncModule
from altscore.borrower_central.model.integrations.sat import SatIntegrationAsyncModule, SatIntegrationSyncModule
from altscore.borrower_central.model.integrations.sri import SriIntegrationAsyncModule, SriIntegrationSyncModule
from altscore.borrower_central.model.automations import AutomationsAsyncModule, AutomationsSyncModule
from altscore.borrower_central.model.stages import StagesAsyncModule, StagesSyncModule
from altscore.borrower_central.model.risk_ratings import RiskRatingsAsyncModule, RiskRatingsSyncModule
from altscore.borrower_central.model.usecases import UsecasesAsyncModule, UsecasesSyncModule
from altscore.borrower_central.model.metrics import MetricsAsyncModule, MetricsSyncModule
from altscore.borrower_central.model.policy_policies import PolicyAsyncModule, PolicySyncModule
from altscore.borrower_central.model.kpis import KpisAsyncModule, KpisSyncModule
from altscore.borrower_central.model.steps import StepsAsyncModule, StepsSyncModule
from altscore.borrower_central.model.list_of_similar import ListOfSimilarAsyncModule, ListOfSimilarSyncModule
from altscore.borrower_central.model.execution_batches import ExecutionBatchAsyncModule, ExecutionBatchSyncModule
from altscore.borrower_central.model.cms_settings import CMSSettingsAsyncModule, CMSSettingsSyncModule


class BorrowerCentralAsync:
    def __init__(self, altscore_client):
        self.addresses = AddressesAsyncModule(altscore_client)
        self.authorizations = AuthorizationsAsyncModule(altscore_client)
        self.automations = AutomationsAsyncModule(altscore_client)
        self.borrowers = BorrowersAsyncModule(altscore_client)
        self.borrower_fields = BorrowerFieldsAsyncModule(altscore_client)
        self.metrics = MetricsAsyncModule(altscore_client)
        self.data_models = DataModelAsyncModule(altscore_client)
        self.documents = DocumentsAsyncModule(altscore_client)
        self.stages = StagesAsyncModule(altscore_client)
        self.risk_ratings = RiskRatingsAsyncModule(altscore_client)
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
        self.store_secrets = SecretsAsyncModule(altscore_client)
        self.evaluators = EvaluatorAsyncModule(altscore_client)
        self.forms = FormsAsyncModule(altscore_client)
        self.alerts = AlertsAsyncModule(altscore_client)
        self.rules = RulesAsyncModule(altscore_client)
        self.policies = PolicyAsyncModule(altscore_client)
        self.sat_integration = SatIntegrationAsyncModule(altscore_client)
        self.sri_integration = SriIntegrationAsyncModule(altscore_client)
        self.usecases = UsecasesAsyncModule(altscore_client)
        self.kpis = KpisAsyncModule(altscore_client)
        self.steps = StepsAsyncModule(altscore_client)
        self.list_of_similar = ListOfSimilarAsyncModule(altscore_client)
        self.execution_batches = ExecutionBatchAsyncModule(altscore_client)
        self.cms_settings = CMSSettingsAsyncModule(altscore_client)
        self.communications = CommunicationsAsyncModule(altscore_client)


class BorrowerCentralSync:
    def __init__(self, altscore_client):
        self.addresses = AddressesSyncModule(altscore_client)
        self.authorizations = AuthorizationsSyncModule(altscore_client)
        self.automations = AutomationsSyncModule(altscore_client)
        self.borrowers = BorrowersSyncModule(altscore_client)
        self.borrower_fields = BorrowerFieldsSyncModule(altscore_client)
        self.metrics = MetricsSyncModule(altscore_client)
        self.data_models = DataModelSyncModule(altscore_client)
        self.documents = DocumentsSyncModule(altscore_client)
        self.stages = StagesSyncModule(altscore_client)
        self.risk_ratings = RiskRatingsSyncModule(altscore_client)
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
        self.store_secrets = SecretsSyncModule(altscore_client)
        self.evaluators = EvaluatorSyncModule(altscore_client)
        self.forms = FormsSyncModule(altscore_client)
        self.alerts = AlertsSyncModule(altscore_client)
        self.rules = RulesSyncModule(altscore_client)
        self.policies = PolicySyncModule(altscore_client)
        self.sat_integration = SatIntegrationSyncModule(altscore_client)
        self.sri_integration = SriIntegrationSyncModule(altscore_client)
        self.usecases = UsecasesSyncModule(altscore_client)
        self.kpis = KpisSyncModule(altscore_client)
        self.steps = StepsSyncModule(altscore_client)
        self.list_of_similar = ListOfSimilarSyncModule(altscore_client)
        self.execution_batches = ExecutionBatchSyncModule(altscore_client)
        self.cms_settings = CMSSettingsSyncModule(altscore_client)
        self.communications = CommunicationsSyncModule(altscore_client)
