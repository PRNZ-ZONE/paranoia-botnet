from src.base.pyrogram import PyrogramFunction
from src.storages import SessionStorage


class Addon(PyrogramFunction):
    description = "Reinitialize the sessions"
    shared_addon = True

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)

    async def execute_clients(self, **kwargs) -> None:
        await self.session_storage.reinitialize()
