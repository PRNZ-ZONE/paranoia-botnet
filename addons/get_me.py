from src.base.pyrogram import PyrogramFunction
from src.storages import SessionStorage


class Addon(PyrogramFunction):
    description = "Gather information about the clients"

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)

        self.strings = {
            "logged_in": "Session {sid} logged in as @{username} ({id})",
        }

    async def prepare_clients(self, **kwargs) -> None:
        pass

    async def execute_clients(self, **kwargs) -> None:
        for sid, client in self.clients.items():
            me = await client.get_me()

            self.console.log(
                self.strings["logged_in"].format(
                    sid=sid,
                    username=me.username,
                    id=me.id,
                )
            )
