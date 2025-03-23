from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
import datetime as dt
import httpx
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async


class BotState(BaseModel):
    current_node: str = Field(alias="currentNode")
    current_flow: str = Field(alias="currentFlow")
    updated_at: dt.datetime = Field(alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ConversationAPIDTO(BaseModel):
    """DTO for conversation API responses"""
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    connector_id: str = Field(alias="connectorId")
    channel_customer_id: str = Field(alias="channelCustomerId")
    state: str = Field(alias="state")
    current_human_agent_id: Optional[str] = Field(None, alias="currentHumanAgentId")  # Fixed alias to be consistent
    current_ai_agent_id: Optional[str] = Field(None, alias="currentAIAgentId")
    bot_state: Optional[BotState] = Field(None, alias="botState")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ConversationCreate(BaseModel):
    borrower_id: str = Field(alias="borrowerId")
    connector_id: str = Field(alias="connectorId")
    channel_customer_id: str = Field(alias="channelCustomerId")
    state: Optional[str] = Field(alias="state", default=None)
    current_human_agent_id: Optional[str] = Field(alias="currentHumanAgentId",
                                                  default=None)  # Fixed alias to be consistent
    current_ai_agent_id: Optional[str] = Field(alias="currentAIAgentId", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ConversationUpdate(BaseModel):
    state: Optional[str] = Field(alias="state", default=None)
    current_human_agent_id: Optional[str] = Field(alias="currentHumanAgentId",
                                                  default=None)  # Fixed alias to be consistent
    current_ai_agent_id: Optional[str] = Field(alias="currentAIAgentId", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class BotStateUpdate(BaseModel):
    current_node: Optional[str] = Field(alias="currentNode", default=None)
    current_flow: Optional[str] = Field(alias="currentFlow", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class ConversationSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/conversations", header_builder, renew_token,
                         ConversationAPIDTO.model_validate(data))

    @retry_on_401
    def put_bot_state(self, current_node: str, current_flow: str):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.put(
                f"/{self.data.id}/bot-state",
                headers=self.build_headers(),
                json=BotStateUpdate(
                    current_node=current_node, current_flow=current_flow
                ).model_dump(
                    by_alias=True, exclude_unset=True, exclude_none=True
                ),
                timeout=120
            )
            raise_for_status_improved(response)

    @property
    def bot_state(self):
        return self.data.bot_state


class ConversationAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/conversations", header_builder, renew_token,
                         ConversationAPIDTO.model_validate(data))

    @retry_on_401_async
    async def put_bot_state(self, current_node: str, current_flow: str):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.put(
                f"/{self.data.id}/bot-state",
                headers=self.build_headers(),
                json=BotStateUpdate(
                    current_node=current_node, current_flow=current_flow
                ).model_dump(
                    by_alias=True, exclude_unset=True, exclude_none=True
                ),
                timeout=120
            )
            raise_for_status_improved(response)

    @property
    def bot_state(self):
        return self.data.bot_state


class ConversationSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=ConversationSync, retrieve_data_model=ConversationAPIDTO,
                         create_data_model=ConversationCreate, update_data_model=ConversationUpdate,
                         resource="/conversational/conversations")

    @retry_on_401
    def find_one_by_connector_and_customer_id(self, connector_id: Optional[str] = None,
                                              channel_customer_id: Optional[str] = None):
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                f"{self.resource}/commands/find-by-connector-and-customer-id",
                json={"connectorId": connector_id, "channelCustomerId": channel_customer_id},
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return self.retrieve(response.json()["id"])


class ConversationAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=ConversationAsync, retrieve_data_model=ConversationAPIDTO,
                         create_data_model=ConversationCreate, update_data_model=ConversationUpdate,
                         resource="/conversational/conversations")

    @retry_on_401_async
    async def find_one_by_connector_and_customer_id(self, connector_id: Optional[str] = None,
                                                    channel_customer_id: Optional[str] = None):
        async with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                f"{self.resource}/commands/find-by-connector-and-customer-id",
                json={"connectorId": connector_id, "channelCustomerId": channel_customer_id},
                headers=self.build_headers(),
                timeout=120
            )
            if response.status_code == 404:
                return None
            raise_for_status_improved(response)
            return await self.retrieve(response.json()["id"])
