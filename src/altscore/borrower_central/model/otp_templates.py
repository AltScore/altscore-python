from pydantic import BaseModel, Field
from altscore.borrower_central.model.generics import GenericSyncResource, GenericAsyncResource, \
    GenericSyncModule, GenericAsyncModule
from typing import Optional, Dict


class OTPTemplateAPIDTO(BaseModel):
    id: str = Field(alias="id")
    channel: str = Field(alias="channel")
    label: str = Field(alias="label")
    lang: Optional[str] = Field(None, alias="lang")
    sender: Optional[str] = Field(None, alias="sender")
    subject: Optional[str] = Field(None, alias="subject")
    title: Optional[str] = Field(None, alias="title")
    header_logo: Optional[str] = Field(None, alias="headerLogo")
    header_logo_height: Optional[str] = Field(alias="headerLogoHeight", default="40px")
    pre_otp_blurb: Optional[str] = Field(None, alias="preOtpBlurb")
    pos_otp_blurb: Optional[str] = Field(None, alias="posOtpBlurb")
    did_not_ask_message: Optional[str] = Field(None, alias="didNotAskMessage")
    footer_blurb: Optional[str] = Field(None, alias="footerBlurb")
    footer_link: Optional[str] = Field(None, alias="footerLink")
    footer_link_label: Optional[str] = Field(None, alias="footerLinkLabel")
    footer_slogan: Optional[str] = Field(None, alias="footerSlogan")
    footer_logo: Optional[str] = Field(None, alias="footerLogo")
    created_at: str = Field(alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class CreateOTPTemplateDTO(BaseModel):
    channel: str = Field(alias="channel")
    label: str = Field(alias="label")
    lang: Optional[str] = Field(None, alias="lang")
    sender: Optional[str] = Field(None, alias="sender")
    subject: Optional[str] = Field(None, alias="subject")
    title: Optional[str] = Field(None, alias="title")
    header_logo: Optional[str] = Field(None, alias="headerLogo")
    header_logo_height: Optional[str] = Field(alias="headerLogoHeight", default="40px")
    pre_otp_blurb: Optional[str] = Field(None, alias="preOtpBlurb")
    pos_otp_blurb: Optional[str] = Field(None, alias="posOtpBlurb")
    did_not_ask_message: Optional[str] = Field(None, alias="didNotAskMessage")
    footer_blurb: Optional[str] = Field(None, alias="footerBlurb")
    footer_link: Optional[str] = Field(None, alias="footerLink")
    footer_link_label: Optional[str] = Field(None, alias="footerLinkLabel")
    footer_slogan: Optional[str] = Field(None, alias="footerSlogan")
    footer_logo: Optional[str] = Field(None, alias="footerLogo")

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }


class OTPTemplatesSync(GenericSyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "otp-templates",header_builder, renew_token, OTPTemplateAPIDTO.model_validate(data))


class OTPTemplatesAsync(GenericAsyncResource):

    def __init__(self, base_url, header_builder, renew_token, data: Dict):
        super().__init__(base_url, "otp-templates",header_builder, renew_token, OTPTemplateAPIDTO.model_validate(data))


class OTPTemplatesSyncModule(GenericSyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         sync_resource=OTPTemplatesSync,
                         retrieve_data_model=OTPTemplateAPIDTO,
                         create_data_model=CreateOTPTemplateDTO,
                         update_data_model=CreateOTPTemplateDTO,
                         resource="otp-templates")


class OTPTemplatesAsyncModule(GenericAsyncModule):

    def __init__(self, altscore_client):
        super().__init__(altscore_client,
                         async_resource=OTPTemplatesAsync,
                         retrieve_data_model=OTPTemplateAPIDTO,
                         create_data_model=CreateOTPTemplateDTO,
                         update_data_model=CreateOTPTemplateDTO,
                         resource="otp-templates")
