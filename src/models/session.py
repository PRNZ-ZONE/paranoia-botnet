from typing import Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field
from pyrogram import Client as PyrogramClient
from telethon import TelegramClient as TelethonClient

from src.enums import SessionType


class Session(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    session_id: str = Field(default_factory=lambda: str(uuid4()))
    session_type: SessionType
    session: Union[TelethonClient, PyrogramClient]
    filename: Optional[str] = None
    is_connected: bool = False
    in_use: bool = False
