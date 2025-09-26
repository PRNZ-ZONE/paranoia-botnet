import json
from pathlib import Path
from typing import Dict, Optional

from pyrogram import Client as PyrogramClient
from telethon import TelegramClient as TelethonClient
from telethon.sessions import StringSession

from src.base import BaseFunction
from src.enums import SessionType
from src.generators import Application
from src.models import Session

from .setting_storage import settings


class SessionStorage(BaseFunction):
    def __init__(self) -> None:
        super().__init__()

        self.strings = {
            "initialize_sessions": "Initialize sessions",
            "initializing_sessions": "Initializing sessions",
            "load_sessions": "Load sessions",
            "initialize_sessions_success": "Initialized sessions",
            "initialize_sessions_failed": "Failed to initialize sessions",
            "load_sessions_success": "Loaded sessions",
            "load_sessions_failed": "Failed to load sessions",
            "ok_bye": "OK, bye",
            "loaded": "Loaded",
            "failed_to_init": "Failed to init",
            "loading": "Loading",
            "loading_sessions": "Loading sessions",
            "reinitializing_sessions": "Reinitializing sessions",
            "application_use": "Do you want to use the custom application for all clients (experimental)?",
            "failed_to_load_application": "Failed to load application {app_file}",
            "saving_application": "Saving application data for {fname}",
            "loading_application": "Loading application data for {fname}",
            "removed_bad_session_file": "Removed bad session file {fname}",
        }

        self.settings = settings
        self.api_id = self.settings.api_id
        self.api_hash = self.settings.api_hash
        self.application_use: bool = False
        self.sessions_dir = Path(self.settings.sessions_dir)
        self._sessions: Dict[str, Session] = {}

        initialize_choice = self.prompt.ask(
            self.strings["initialize_sessions"],
            choices=["y", "n"],
        )

        app_choice = self.prompt.ask(
            self.strings["application_use"],
            choices=["y", "n"],
        )

        self.application_use = app_choice == "y"
        if initialize_choice == "y":
            self.load_sessions()
        else:
            self.console.log(self.strings["ok_bye"])

    async def reinitialize(self) -> None:
        self.console.log(self.strings["reinitializing_sessions"])
        self.load_sessions()
        await self.initialize_sessions()

    def _app_file(self, file: Path) -> Path:
        return file.with_suffix(".app.json")

    def _save_application(self, file: Path, app: Application) -> None:
        app_data = {
            "device_model": app.device(),
            "system_version": app.sdk(),
            "app_version": app.app_version(),
            "lang_code": app.system_lang_code(),
            "lang_pack": app.lang_pack,
            "system_lang_code": app.system_lang_code(),
            "system_lang_pack": app.lang_pack,
        }

        self.console.log(
            self.strings["saving_application"].format(fname=file.name),
        )

        with self._app_file(file).open("w", encoding="utf-8") as f:
            json.dump(app_data, f, indent=2)

    def _load_application(self, file: Path) -> Optional[dict]:
        app_file = self._app_file(file)
        if app_file.exists():
            try:
                self.console.log(
                    self.strings["loading_application"].format(fname=file.name),
                )
                return json.loads(app_file.read_text(encoding="utf-8"))
            except Exception:
                self.console.log(
                    self.strings["failed_to_load_application"].format(
                        app_file=app_file
                    ),
                )
        return None

    def _get_application_data(self, file: Path) -> dict:
        app_data = self._load_application(file)
        if not app_data:
            app = Application()
            self._save_application(file, app)
            app_data = self._load_application(file) or {}
        return app_data

    def load_sessions(self) -> None:
        if not self.sessions_dir.exists():
            return

        for file in self.sessions_dir.glob("*.session"):
            self.console.log(
                "{loading} {fname}".format(
                    loading=self.strings["loading"],
                    fname=file.name,
                )
            )

            session = self.telethon_session(file) or self.pyrogram_session(file)

            if session:
                self._sessions[file.name] = session

    def telethon_session(self, file: Path) -> Optional[Session]:
        session_string = file.read_text().strip()
        if len(session_string) != 353:
            return None

        extra_kwargs = {}
        if self.application_use:
            extra_kwargs = self._sanitize_kwargs(
                "telethon", self._get_application_data(file)
            )

        client = TelethonClient(
            session=StringSession(session_string),
            api_id=self.api_id,
            api_hash=self.api_hash,
            **extra_kwargs,
        )

        return Session(
            session_type=SessionType.TELETHON,
            session=client,
            filename=file.name,
        )

    def pyrogram_session(self, file: Path) -> Optional[Session]:
        session_string = file.read_text().strip()
        if len(session_string) != 362:
            return None

        extra_kwargs = {}
        if self.application_use:
            extra_kwargs = self._sanitize_kwargs(
                "pyrogram", self._get_application_data(file)
            )

        client = PyrogramClient(
            name=file.stem,
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_string=session_string,
            workdir=str(self.sessions_dir),
            **extra_kwargs,
        )

        return Session(
            session_type=SessionType.PYROGRAM,
            session=client,
            filename=file.name,
        )

    async def initialize_sessions(self) -> None:
        with self.console.status(self.strings["initializing_sessions"]):
            for session in list(self.sessions.values()):
                try:
                    if session.session_type == SessionType.TELETHON:
                        await session.session.connect()
                    elif session.session_type == SessionType.PYROGRAM:
                        await session.session.start()

                    session.is_connected = True

                    self.console.log(
                        "{loaded} {stype} session: {fname}".format(
                            loaded=self.strings["loaded"],
                            stype=session.session_type.value,
                            fname=session.filename,
                        )
                    )
                except Exception as e:
                    self.remove_session(session.filename)
                    file_path = self.sessions_dir / session.filename

                    try:
                        file_path.unlink()
                        self.console.log(
                            self.strings["removed_bad_session_file"].format(
                                fname=session.filename
                            )
                        )
                    except FileNotFoundError:
                        pass

                    self.console.log(
                        "{failed} {fname}: {error}".format(
                            failed=self.strings["failed_to_init"],
                            fname=session.filename,
                            error=e,
                        )
                    )

    @property
    def sessions(self) -> Dict[str, Session]:
        return self._sessions

    def get_session(self, session_id: str) -> Session:
        return self._sessions[session_id]

    def add_session(self, session: Session) -> None:
        key = session.filename or session.session_id
        self._sessions[key] = session

    def remove_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def update_session(self, session_id: str, session: Session) -> None:
        self._sessions[session_id] = session

    def clear_sessions(self) -> None:
        self._sessions.clear()

    def _sanitize_kwargs(self, client_type: str, kwargs: dict) -> dict:
        allowed = {
            "telethon": [
                "device_model",
                "system_version",
                "app_version",
                "lang_code",
                "system_lang_code",
            ],
            "pyrogram": [
                "device_model",
                "system_version",
                "app_version",
            ],
        }
        return {k: v for k, v in kwargs.items() if k in allowed.get(client_type, [])}
