import httpx
from typing import Any, Dict, Optional
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async
from altscore.borrower_central.helpers import build_headers

_BASE_PATH = "/v2/workflows"


def _import_payload(
    workflow_data: Dict[str, Any],
    new_label: Optional[str],
    skip_evaluation_rules: bool,
    skip_scorecards: bool,
    skip_rule_trees: bool,
    skip_mapping_tables: bool
) -> Dict[str, Any]:
    return {
        "workflowData": workflow_data,
        "newLabel": new_label,
        "skipEvaluationRules": skip_evaluation_rules,
        "skipScorecards": skip_scorecards,
        "skipRuleTrees": skip_rule_trees,
        "skipMappingTables": skip_mapping_tables
    }


class WorkflowsV2SyncModule:
    """Workflows V2 authoring surface.

    Only the calls a template/provisioning flow needs: import a whole exported
    bundle in one shot, publish it, export one back out, and validate without
    persisting. The graph itself is passed through as raw JSON -- the canonical
    node/edge/task shapes are served live by
    GET /v1/meta/workflows-v2-schema, not pinned here.

    Import and publish require the `workflows.write` permission; export and
    validate require `workflows.read`.
    """

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401
    def import_workflow(
        self,
        workflow_data: Dict[str, Any],
        new_label: Optional[str] = None,
        skip_evaluation_rules: bool = False,
        skip_scorecards: bool = False,
        skip_rule_trees: bool = False,
        skip_mapping_tables: bool = False
    ) -> Dict[str, Any]:
        """Import a workflow and all its tasks from an exported bundle.

        `workflow_data` is the export shape: it must carry a `workflow` key
        (itself carrying `label` and `nodes`) and may carry `tasks`,
        `evaluationRules`, `scorecards`, `ruleTrees` and `mappingTables`.

        The alias is derived from the label and cannot be set. A tenant that
        already holds that alias gets HTTP 409 with code ALIAS_EXISTS -- there
        is no version bump, so callers retrying a provisioning step should
        treat 409 as already-done. The imported workflow lands in DRAFT; call
        publish() to make the alias serve it.
        """
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/import"
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self.build_headers(),
                json=_import_payload(
                    workflow_data, new_label, skip_evaluation_rules,
                    skip_scorecards, skip_rule_trees, skip_mapping_tables
                ),
                timeout=60
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def publish(self, workflow_id: str, lock_token: Optional[str] = None) -> Dict[str, Any]:
        """Publish a DRAFT workflow to ACTIVE.

        Stricter than create: the graph needs at least one node, a start node,
        exactly one end node, and every non-start/end node must resolve a task.
        `lock_token` is only needed when someone holds the alias edit lock; on a
        freshly provisioned tenant there is none.
        """
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/{workflow_id}/publish"
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self.build_headers(),
                json={"lockToken": lock_token},
                timeout=60
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def export(self, workflow_id: str) -> Dict[str, Any]:
        """Export a workflow and its tasks as a bundle importable elsewhere."""
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/{workflow_id}/export"
        with httpx.Client() as client:
            response = client.get(url, headers=self.build_headers(), timeout=60)
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401
    def validate(
        self,
        workflow: Dict[str, Any],
        tasks: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the validation oracle without persisting anything.

        Returns HTTP 200 for any well-formed body; read `valid` and `findings`
        off the response rather than relying on the status code.
        """
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/validate"
        payload: Dict[str, Any] = {"workflow": workflow}
        if tasks is not None:
            payload["tasks"] = tasks
        with httpx.Client() as client:
            response = client.post(url, headers=self.build_headers(), json=payload, timeout=60)
            raise_for_status_improved(response)
            return response.json()


class WorkflowsV2AsyncModule:
    """Async counterpart of WorkflowsV2SyncModule."""

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def renew_token(self):
        self.altscore_client.renew_token()

    def build_headers(self):
        return build_headers(self)

    @retry_on_401_async
    async def import_workflow(
        self,
        workflow_data: Dict[str, Any],
        new_label: Optional[str] = None,
        skip_evaluation_rules: bool = False,
        skip_scorecards: bool = False,
        skip_rule_trees: bool = False,
        skip_mapping_tables: bool = False
    ) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/import"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.build_headers(),
                json=_import_payload(
                    workflow_data, new_label, skip_evaluation_rules,
                    skip_scorecards, skip_rule_trees, skip_mapping_tables
                ),
                timeout=60
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def publish(self, workflow_id: str, lock_token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/{workflow_id}/publish"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.build_headers(),
                json={"lockToken": lock_token},
                timeout=60
            )
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def export(self, workflow_id: str) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/{workflow_id}/export"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.build_headers(), timeout=60)
            raise_for_status_improved(response)
            return response.json()

    @retry_on_401_async
    async def validate(
        self,
        workflow: Dict[str, Any],
        tasks: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.altscore_client._borrower_central_base_url}{_BASE_PATH}/validate"
        payload: Dict[str, Any] = {"workflow": workflow}
        if tasks is not None:
            payload["tasks"] = tasks
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.build_headers(), json=payload, timeout=60)
            raise_for_status_improved(response)
            return response.json()
