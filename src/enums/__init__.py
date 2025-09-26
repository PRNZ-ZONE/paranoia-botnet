from enum import Enum


class SessionType(Enum):
    TELETHON = "telethon"
    PYROGRAM = "pyrogram"


__all__ = ["SessionType"]
