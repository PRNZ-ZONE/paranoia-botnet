from typing import Dict

from pyrogram import Client as PyrogramClient

from src.enums import SessionType
from src.models import Session
from src.storages import SessionStorage

from . import BaseFunction


class PyrogramFunction(BaseFunction):
    def __init__(self, session_storage: SessionStorage):
        super().__init__()

        self.session_storage = session_storage
        self.sessions_count = len(self.clients)

    @property
    def clients(self) -> Dict[str, PyrogramClient]:
        return {
            session.session_id: session.session
            for session in self.session_storage.sessions.values()
            if session.session_type == SessionType.PYROGRAM
        }

    @property
    def shared_clients(self) -> Dict[str, PyrogramClient]:
        return {
            session.session_id: session.session
            for session in self.session_storage.sessions.values()
            if session.session_type == SessionType.PYROGRAM and session.shared
        }

    async def prepare_clients(self, **kwargs) -> None:
        raise NotImplementedError("This method is not implemented")

    async def execute_clients(self, **kwargs) -> None:
        raise NotImplementedError("This method is not implemented")

    def get_client(self, session_id: str) -> PyrogramClient:
        return self.clients[session_id]

    def get_session(self, session_id: str) -> Session:
        return self.session_storage.get_session(session_id)
