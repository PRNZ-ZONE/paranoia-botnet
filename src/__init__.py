from src.storages import AddonStorage, SessionStorage


def setup() -> None:
    pass


async def initialize_botnet() -> None:
    session_storage = SessionStorage()
    await session_storage.initialize_sessions()
    addon_storage = AddonStorage()
    addon_storage.load_addons()
    await addon_storage.run_menu(session_storage)
