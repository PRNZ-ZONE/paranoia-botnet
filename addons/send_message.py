from src.base.pyrogram import PyrogramFunction
from src.storages import SessionStorage


class Addon(PyrogramFunction):
    description = "Gather all clients and send message to someone"

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)
        self.username: str = None
        self.text: str = None

        self.strings = {
            "prompt_username": "Enter username",
            "prompt_text": "Enter text",
            "message_sent": "Session {sid} sent message to @{username} ({id})",
        }

    async def prepare_clients(self, **kwargs) -> None:
        self.username = self.prompt.ask(self.strings["prompt_username"])
        self.text = self.prompt.ask(self.strings["prompt_text"])

    async def execute_clients(self, **kwargs) -> None:
        await self.prepare_clients()

        for sid, client in self.clients.items():
            me = await client.send_message(
                chat_id=self.username,
                text=self.text,
            )

            self.console.log(
                self.strings["message_sent"].format(
                    sid=sid,
                    username=me.chat.username,
                    id=me.chat.id,
                )
            )
