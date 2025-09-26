import uuid
from pathlib import Path

from src.base.pyrogram import PyrogramFunction
from src.generators import SessionManager
from src.storages import SessionStorage


class Addon(PyrogramFunction):
    description = "Convert Pyrogram sessions to Telethon sessions"
    shared_addon = True

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)

        self.strings = {
            "prompt_convert": "Do you want to convert all sessions to Telethon?",
            "skipping_conversion": "Skipping conversion",
            "converted_to_telethon": "Session {uuid} converted to Telethon",
        }

    async def prepare_clients(self, **kwargs) -> None:
        out_dir = Path("sessions/telethon")
        out_dir.mkdir(parents=True, exist_ok=True)

        for session in self.clients.values():
            string = session.session_string

            session_manager = SessionManager.from_pyrogram_string_session(string)
            telethon_string = session_manager.telethon_string_session()

            with open(f"sessions/telethon/{uuid.uuid4()}.session", "w") as f:
                f.write(telethon_string)

            self.console.log(
                self.strings["converted_to_telethon"].format(uuid=uuid.uuid4())
            )

    async def execute_clients(self, **kwargs) -> None:
        ask = self.prompt.ask(
            self.strings["prompt_convert"],
            choices=["y", "n"],
        )
        if ask == "y":
            await self.prepare_clients()
        else:
            self.console.log(self.strings["skipping_conversion"])
