from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime


class MessageIn(BaseModel):
    content: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    assistant: MessageOut
    messages: list[MessageOut]
