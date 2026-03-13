from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class ConversationAPIDTO(BaseModel):
    """DTO for conversation API responses"""
    id: str = Field(alias="id")
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    connector_id: str = Field(alias="connectorId")
    connector_sender_id: Optional[str] = Field(alias="connectorSenderId", default=None)
    channel_user_id: str = Field(alias="channelUserId")
    channel: str = Field(alias="channel")
    state: str = Field(alias="state")
    current_human_agent_id: Optional[str] = Field(alias="currentHumanAgentId", default=None)
    current_ai_agent_id: Optional[str] = Field(alias="currentAIAgentId", default=None)
    bot_state: Optional[Dict[str, Any]] = Field(alias="botState", default=None)
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)
    pending_messages_count: Optional[int] = Field(alias="messagePendingCount", default=0)
    status_chat: Optional[str] = Field(alias="statusChat", default=None)
    last_message_at: Optional[str] = Field(alias="lastMessageAt", default=None)
    notices: Optional[List[Dict[str, Any]]] = Field(alias="notices", default=[])
    is_hidden: Optional[bool] = Field(alias="isHidden", default=False)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ConversationCreate(BaseModel):
    borrower_id: Optional[str] = Field(alias="borrowerId", default=None)
    connector_id: str = Field(alias="connectorId")
    connector_sender_id: str = Field(alias="connectorSenderId")
    channel_user_id: str = Field(alias="channelUserId")
    channel: Optional[str] = Field(alias="channelId", default="whatsapp")
    state: Optional[str] = Field(alias="state", default=None)
    bot_state: Optional[Dict[str, Any]] = Field(alias="botState", default=None)
    current_human_agent_id: Optional[str] = Field(alias="currentHumanAgentId", default=None)
    current_ai_agent_id: Optional[str] = Field(alias="currentAIAgentId", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ConversationUpdate(BaseModel):
    state: Optional[str] = Field(alias="state")
    current_human_agent_id: Optional[str] = Field(alias="currentHumanAgentId")  # Fixed alias to be consistent
    current_ai_agent_id: Optional[str] = Field(alias="currentAIAgentId")
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ConversationSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/conversations", header_builder, renew_token,
                         ConversationAPIDTO.parse_obj(data))


class ConversationAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/conversations", header_builder, renew_token,
                         ConversationAPIDTO.parse_obj(data))


class ConversationSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=ConversationSync, retrieve_data_model=ConversationAPIDTO,
                         create_data_model=ConversationCreate, update_data_model=ConversationUpdate,
                         resource="/conversational/conversations")


class ConversationAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=ConversationAsync, retrieve_data_model=ConversationAPIDTO,
                         create_data_model=ConversationCreate, update_data_model=ConversationUpdate,
                         resource="/conversational/conversations")

