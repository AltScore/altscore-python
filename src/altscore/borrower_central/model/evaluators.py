from typing import Optional, List, Dict, Any
import httpx
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from pydantic import ConfigDict, BaseModel, Field
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async


class EvaluatorAPIDTO(BaseModel):
    id: str = Field(alias="id")
    alias: str = Field(alias="alias")
    version: str = Field(alias="version")
    label: Optional[str] = Field(None, alias="label")
    description: Optional[str] = Field(None, alias="description")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    specs: Dict = Field(alias="specs")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateEvaluatorDTO(BaseModel):
    label: Optional[str] = Field(None, alias="label")
    alias: str = Field(alias="alias")
    version: str = Field(alias="version")
    description: Optional[str] = Field(None, alias="description")
    specs: Dict = Field(alias="specs")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class UpdateEvaluatorDTO(BaseModel):
    label: Optional[str] = Field(None, alias="label")
    description: Optional[str] = Field(None, alias="description")
    specs: Dict = Field(alias="specs")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class Instance(BaseModel):
    reference_id: str = Field(alias="referenceId")
    reference_date: str = Field(alias="referenceDate")
    data: Dict[str, Any] = Field(alias="data", default={})


class Entity(BaseModel):
    entity_id: str = Field(alias="entityId")
    role: Optional[str] = Field(alias="role", default=None)
    character: Optional[str] = Field(alias="character", default=None)
    data: Dict[str, Any] = Field(alias="data", default={})


class EvaluatorInput(BaseModel):
    instance: Instance = Field(alias="instance")
    entities: List[Entity] = Field(alias="entities")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class BusinessRuleOutput(BaseModel):
    id: Optional[str] = Field(alias="id", default=None)
    order: int = Field(alias="order")
    code: str = Field(alias="code")
    label: str = Field(alias="label")
    value: str = Field(alias="value")
    alert_level: Optional[int] = Field(alias="alertLevel", default=None)
    # hit can be None if the rule cannot be evaluated due to missing fields
    hit: Optional[bool] = Field(alias="hit", default=None)
    model_config = ConfigDict(populate_by_name=True, allow_population_by_alias=True)


class ScoreOutput(BaseModel):
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    value: float = Field(alias="value")
    max_value: Optional[float] = Field(alias="maxValue", default=None)
    model_config = ConfigDict(populate_by_name=True, allow_population_by_alias=True)


class ScoreCardRuleOutput(BaseModel):
    field: str = Field(alias="field")
    order: int = Field(alias="order")
    value: Any = Field(None, alias="value")
    bucket: int = Field(alias="bucket")
    points: int = Field(alias="points")
    max_points: int = Field(alias="maxPoints")
    label: str = Field(alias="label")
    bucket_label: str = Field(alias="bucketLabel")
    model_config = ConfigDict(populate_by_name=True, allow_population_by_alias=True)


class MetricOutput(BaseModel):
    key: str = Field(alias="key")
    label: str = Field(alias="label")
    value: Any = Field(None, alias="value")
    metadata: Optional[Dict] = Field(alias="metadata", default=None)


class EvaluatorOutput(BaseModel):
    score: Optional[ScoreOutput] = Field(alias="score", default=None)
    scorecard: List[ScoreCardRuleOutput] = Field(alias="scorecard", default=[])
    metrics: List[MetricOutput] = Field(alias="metrics", default=[])
    rules: List[BusinessRuleOutput] = Field(alias="rules", default=[])
    decision: str = Field(alias="decision")
    model_config = ConfigDict(populate_by_name=True, allow_population_by_alias=True)


class EvaluatorOutputError(BaseModel):
    detail: str = Field(alias="detail")
    traceback: List[str] = Field(alias="traceback")
    model_config = ConfigDict(populate_by_name=True, allow_population_by_alias=True)


class EvaluatorSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "evaluators", header_builder, renew_token, EvaluatorAPIDTO.model_validate(data))

    @retry_on_401
    def evaluate(self, evaluator_input: EvaluatorInput) -> EvaluatorOutput | EvaluatorOutputError:
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/{self.resource}/{self.data.id}/evaluate",
                headers=self._header_builder(),
                json=evaluator_input.model_dump(by_alias=True),
                timeout=300
            )
            raise_for_status_improved(response)
            if "traceback" in response.json():
                return EvaluatorOutputError.model_validate(response.json())
            else:
                return EvaluatorOutput.model_validate(response.json())


class EvaluatorAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "evaluators", header_builder, renew_token, EvaluatorAPIDTO.model_validate(data))

    @retry_on_401_async
    async def evaluate(self, evaluator_input: EvaluatorInput) -> EvaluatorOutput | EvaluatorOutputError:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.resource}/{self.data.id}/evaluate",
                headers=self._header_builder(),
                json=evaluator_input.model_dump(by_alias=True),
                timeout=300
            )
            raise_for_status_improved(response)
            if "traceback" in response.json():
                return EvaluatorOutputError.model_validate(response.json())
            else:
                return EvaluatorOutput.model_validate(response.json())


class EvaluatorSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=EvaluatorSync,
                         retrieve_data_model=EvaluatorAPIDTO,
                         create_data_model=CreateEvaluatorDTO,
                         update_data_model=UpdateEvaluatorDTO,
                         resource="evaluators")

    def renew_token(self):
        self.altscore_client.renew_token()

    @retry_on_401
    def evaluate(
            self, evaluator_input: Dict, evaluator_id: Optional[str] = None,
            evaluator_alias: Optional[str] = None, evaluator_version: Optional[str] = None
    ) -> EvaluatorOutput | EvaluatorOutputError:

        if evaluator_id is not None:
            url = f"{self.altscore_client._borrower_central_base_url}/v1/evaluators/{evaluator_id}/evaluate"
        elif evaluator_alias is not None and evaluator_version is not None:
            url = f"{self.altscore_client._borrower_central_base_url}/v1/evaluators/{evaluator_alias}/{evaluator_version}/evaluate"
        else:
            raise ValueError("either evaluator_id or evaluator_alias and evaluator_version must be provided")

        with httpx.Client() as client:
            response = client.post(
                url,
                headers=self.build_headers(),
                json=EvaluatorInput.model_validate(evaluator_input).model_dump(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            if "traceback" in response.json():
                return EvaluatorOutputError.model_validate(response.json())
            else:
                return EvaluatorOutput.model_validate(response.json())


class EvaluatorAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=EvaluatorAsync,
                         retrieve_data_model=EvaluatorAPIDTO,
                         create_data_model=CreateEvaluatorDTO,
                         update_data_model=UpdateEvaluatorDTO,
                         resource="evaluators")

    def renew_token(self):
        self.altscore_client.renew_token()

    @retry_on_401_async
    async def evaluate(
            self, evaluator_input: Dict, evaluator_id: Optional[str] = None,
            evaluator_alias: Optional[str] = None, evaluator_version: Optional[str] = None
    ) -> EvaluatorOutput | EvaluatorOutputError:

        if evaluator_id is not None:
            url = f"{self.altscore_client._borrower_central_base_url}/v1/evaluators/{evaluator_id}/evaluate"
        elif evaluator_alias is not None and evaluator_version is not None:
            url = f"{self.altscore_client._borrower_central_base_url}/v1/evaluators/{evaluator_alias}/{evaluator_version}/evaluate"
        else:
            raise ValueError("either evaluator_id or evaluator_alias and evaluator_version must be provided")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.build_headers(),
                json=EvaluatorInput.model_validate(evaluator_input).model_dump(by_alias=True),
                timeout=120
            )
            raise_for_status_improved(response)
            if "traceback" in response.json():
                return EvaluatorOutputError.model_validate(response.json())
            else:
                return EvaluatorOutput.model_validate(response.json())
