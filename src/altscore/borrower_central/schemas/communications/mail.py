from typing import List, Optional
from mimetypes import guess_type

from pydantic import BaseModel, EmailStr

class Email(BaseModel):
    email: EmailStr

class Attachment(BaseModel):
    type: str
    filename: str
    content: str

    model_config = {
        'populate_by_name': True,
        'alias_generator': None,
        'str_strip_whitespace': True
    }

class MailBody(BaseModel):
    to: List[Email]
    cc: Optional[List[Email]] = []
    bcc: Optional[List[Email]] = []
    subject: str
    content: str
    attachments: List[Attachment] = []

    def add_attachment(self, filename: str, content: str, file_type = None):
        attachment_type = file_type if file_type is not None else guess_type(filename)[0]
        if attachment_type is None:
            raise Exception("No attachment type specified nor could be guessed")

        self.attachments.append(
            Attachment(type=attachment_type, filename=filename, content=content)
        )

    def to_dict(self):
        return {
            'to': [m.model_dump() for m in self.to],
            'cc': [m.model_dump() for m in self.cc],
            'bcc': [m.model_dump() for m in self.bcc],
            'subject': self.subject,
            'content': self.content,
            'attachments': [a.model_dump(by_alias=True) for a in self.attachments]
        }