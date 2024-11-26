from pydantic import Field
from typing import List, Optional

from pydantic import BaseModel, EmailStr

class Email(BaseModel):
    email: EmailStr

class Attachment(BaseModel):
    type_: str = Field(alias='type')
    filename: str
    content: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        allow_population_by_alias = True

class MailBody(BaseModel):
    to: List[Email]
    cc: Optional[List[Email]] = []
    bcc: Optional[List[Email]] = []
    subject: str
    content: str
    attachments: List[Attachment] = []

    def add_attachment(self, type_: str, filename: str, content: str):
        self.attachments.append(
            Attachment(type_=type_, filename=filename, content=content)
        )

    def to_dict(self):
        return {
            'to': [m.dict() for m in self.to],
            'cc': [m.dict() for m in self.cc],
            'bcc': [m.dict() for m in self.bcc],
            'subject': self.subject,
            'content': self.content,
            'attachments': [a.dict(by_alias=True) for a in self.attachments]
        }