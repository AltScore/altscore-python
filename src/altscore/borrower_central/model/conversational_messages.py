from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule


class MessageAPIDTO(BaseModel):
    """DTO for message API responses"""
    id: str = Field(alias="id")
    borrower_id: str = Field(alias="borrowerId")
    channel: str = Field(alias="channel")
    channel_customer_id: str = Field(alias="channelCustomerId")
    conversation_id: str = Field(alias="conversationId")
    content: str = Field(alias="content")
    sender_type: str = Field(alias="senderType")
    sender_id: Optional[str] = Field(None, alias="senderId")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    created_at: str = Field(alias="createdAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class MessageCreate(BaseModel):
    channel: str = Field(alias="channel")
    conversation_id: str = Field(alias="conversationId")
    borrower_id: str = Field(alias="borrowerId")
    content: str = Field(alias="content")
    channel_customer_id: str = Field(alias="channelCustomerId")
    sender_type: str = Field(alias="senderType")
    sender_id: Optional[str] = Field(alias="senderId", default=None)
    metadata: Optional[Dict[str, Any]] = Field(alias="metadata", default=None)

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class MessageSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/messages", header_builder, renew_token,
                         MessageAPIDTO.model_validate(data))


class MessageAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "/conversational/messages", header_builder, renew_token,
                         MessageAPIDTO.model_validate(data))


class MessageSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, sync_resource=MessageSync, retrieve_data_model=MessageAPIDTO,
                         create_data_model=MessageCreate, update_data_model=None,
                         resource="/conversational/messages")


class MessageAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client, async_resource=MessageSync, retrieve_data_model=MessageAPIDTO,
                         create_data_model=MessageCreate, update_data_model=None,
                         resource="/conversational/messages")
