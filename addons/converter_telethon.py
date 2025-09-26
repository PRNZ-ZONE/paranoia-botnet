import uuid
from pathlib import Path

from src.base.telethon import TelethonFunction
from src.generators import SessionManager
from src.storages import SessionStorage


class Addon(TelethonFunction):
    description = "Convert Telethon sessions to Pyrogram sessions"
    shared_addon = True

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)

        self.strings = {
            "prompt_convert": "Do you want to convert all sessions to Pyrogram?",
            "skipping_conversion": "Skipping conversion",
            "converted_to_pyrogram": "Session {uuid} converted to Pyrogram",
        }

    async def prepare_clients(self, **kwargs) -> None:
        out_dir = Path("sessions/pyrogram")
        out_dir.mkdir(parents=True, exist_ok=True)

        for session in self.clients.values():
            string = session.session.save()

            session_manager = SessionManager.from_telethon_string_session(string)
            pyrogram_string = session_manager.pyrogram_string_session()

            with open(f"sessions/pyrogram/{uuid.uuid4()}.session", "w") as f:
                f.write(pyrogram_string)

            self.console.log(
                self.strings["converted_to_pyrogram"].format(uuid=uuid.uuid4())
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
